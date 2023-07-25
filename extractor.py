# ML MODEL IMPORTS
import mcl_ca as mclc
import mcl_gstin as mclg
import mcl_legal as mcll
import mcl_pan as mclp
import mcl_attorney as mcla
import mcl_dsc as mcld
import mcl_workcap as mclw
import nit
import mcl_undertaking as mcl_under
import civil_attorney as civ_attorney

# PACKAGES IMPORT
import threading
import uuid
import time
import json
import os
import pandas as pd
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from pymongo import MongoClient

# flask service project_nlp.service

app = Flask(__name__)
cors = CORS(app)

DB_KEY = os.getenv('DB_API')
JWT_SECRET = os.getenv('JWT_SECRET')

#  AUTHENTICATION SETUP

app.config["JWT_SECRET_KEY"] = JWT_SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

#  DATABASE SETUP

try:
    client = MongoClient(DB_KEY)
except:
    print("DB not connectd")

db = client.mcl_bid

#  COLLECTIONS

users = db.users
reports = db.reports


# AUTHENTICATION ROUTES

# @app.route('/signup')
# def signup():

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route('/')
def greet():
    return "hello !"


@app.route('/home')
def home():
    return "home page"


@app.route('/signup', methods=["POST"])
def signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user_obj = users.find_one({"email": email})
    if user_obj:
        return {"msg": "User already exist !"}

    users.insert_one({"email": email, "password": password, "reports": []})
    access_token = create_access_token(identity=email)
    response = {"access_token": access_token}
    return response


@app.route('/login', methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user_obj = users.find_one({"email": email})
    if not user_obj:
        return {"msg": "Wrong email or password !"}

    if user_obj == None or password != user_obj['password']:
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=email)
    response = {"access_token": access_token}
    return response


@app.route('/logout', methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


class Extractor:
    def extract_pan(self, filepath):
        return mclp.getPAN(filepath)

    def extract_gstin(self, filepath):
        return mclg.getGSTIN(filepath)

    def extract_info_from_legal(self, filepath):
        return mcll.extract_from_legal(filepath)


class CivilExtractor(Extractor):
    nit_desc = {}
    gtc = ""

    def __init__(self, nit_path):
        n = nit.CivilNITDoc(nit_path)
        self.nit_desc = n.extract_info()

    def extract_info_from_ca(self, filepath):
        return mclc.extract_from_CA(filepath)

    def extract_attorney(self, filepath):
        return civ_attorney.extract_attorney(filepath)

    def extract_local_content(self, filepath):
        return mcl_under.extract_local_content(filepath)


class CMCExtractor(Extractor):
    nit_desc = {}
    gtc = ""

    def __init__(self, nit_path, gtc_path) -> None:
        n = nit.CMCNITDoc(nit_path)
        self.nit_desc = n.extract_info()
        self.gtc = mcl_under.extract_gtc(gtc_path)

    def extract_from_affidavit(self, filepath):
        return mcla.extract_attorney_desc(filepath, self.nit_desc["Work Description"])

    def extract_from_dsc(self, filepath):
        return mcld.extract_from_dsc(filepath)

    def extract_workcap(self, filepath):
        return mclw.extract_workcap(filepath)

    def check_undertaking(self, filepath):
        return mcl_under.compare_genuineness(filepath, self.gtc)


def background_processing(links, email, bid_id, type):
    # STATUS => 0 loading, 1 finished

    final_output = {}

    users.update_one({"email": email, "reports._id": bid_id}, {
                     "$set": {"reports.$.status": "1"}})

    if type == "cmc":
        extr_obj = CMCExtractor(links["nit_link"], links["gtc_link"])
        final_output = {
            'nit_desc': extr_obj.nit_desc,
            'pan': extr_obj.extract_pan(links['pan_link']),
            'gstin': extr_obj.extract_gstin(links['gstin_link']),
            'attorney': extr_obj.extract_from_affidavit(links['attorney_link']),
            'legal': extr_obj.extract_info_from_legal(links['legal_link']),
            'dsc': extr_obj.extract_from_dsc(links['dsc_link']),
            'workcap': extr_obj.extract_workcap(links['workcap_link']),
            'undertaking': extr_obj.check_undertaking(links['under_link']),
        }
        del extr_obj
    elif type == "civil":
        extr_obj = CivilExtractor(links['nit_link'])
        ca_output = extr_obj.extract_info_from_ca(links['ca_link'])
        final_output = {
            'nit_desc': extr_obj.nit_desc,
            'ca_name': ca_output['CA Name'],
            'pan': extr_obj.extract_pan(links['pan_link']),
            'gstin': extr_obj.extract_gstin(links['gstin_link']),
            'legal': extr_obj.extract_info_from_legal(links['legal_link']),
            'udin': ca_output['UDIN No.'],
            'company_audited': ca_output['Company audited'],
            'type_of_work': ca_output['Type of work done'],
            'relevent_work_experience': ca_output['Relevant Work Experience'].to_dict(orient='records'),
            'local_content': extr_obj.extract_local_content(links['civil_local'])
        }
        del extr_obj
    # STORE RESULT IN DATABASE

    users.update_one({"email": email, "reports._id": bid_id}, {"$set": {'reports.$.output':
                     json.dumps(final_output), 'reports.$.status': "0"}}, upsert=False)


@app.route('/result', methods=['POST'])
@jwt_required()
def combined_func():
    current_user_email = get_jwt_identity()
    bid_id = request.json.get("bid_id", None)
    links = request.json.get("links", None)
    extractor_type = request.json.get("type", None)
    users.update_one({"email": current_user_email, "reports._id": bid_id}, {
                     "$set": {"reports.$.links": links}})

    links = json.loads(links)
    print(links)
    print(extractor_type)
    print("----------------")
    # print(links)
    # if (links.get("pan_link") and links.get("gstin_link") and links.get("ca_link") and links.get("legal_link") and links.get("attorney_link") and links.get("dsc_link") and links.get("workcap_link") and links.get("attorney_nit_desc")):
    #     # everything fine
    # else :
    #     return "0"
    #     # SINGLE THREAD
    try:
        thread = threading.Thread(target=background_processing, kwargs={
            'links': links, 'email': current_user_email, "bid_id": bid_id, 'type': extractor_type})
        thread.start()
    except:
        print("error in threading")
    return "1"


@app.route('/bidder_list', methods=['GET'])
@jwt_required()
def getBidderList():
    current_user_email = get_jwt_identity()
    bidder_list = users.find_one({"email": current_user_email})
    return {"bidder_list": bidder_list["reports"]}


@app.route('/details', methods=['POST'])
@jwt_required()
def saveDetailToDB():
    current_user_email = get_jwt_identity()
    data = request.json.get("details", None)
    unique_id = uuid.uuid4().hex
    users.update_one({"email": current_user_email}, {
                     "$push": {"reports": {"_id": unique_id, "details": data}}})
    return {"bid_id": unique_id}


@app.route('/reports')
@jwt_required()
def getReports():
    current_user_email = get_jwt_identity()
    req_user = users.find_one({"email": current_user_email})
    return {"reports": req_user['reports'], "status": req_user["status"], "details": req_user["details"]}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
