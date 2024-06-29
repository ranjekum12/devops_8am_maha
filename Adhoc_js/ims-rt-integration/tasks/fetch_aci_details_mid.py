import requests
import json
#from read_access_token import retrieve_token
from utils.vault_helper import read_secret 
import logging
import argparse

logging.basicConfig(level=logging.INFO)

def _check_instance_exists(aci_base_url, aci_instance_id, headers):
    try:
        url = url = aci_base_url + "instances/" + aci_instance_id
        res = requests.get(url, headers=headers)
        resp = json.loads(res.content)
        if res.status_code == 404 or resp['status'] != 'online':
            return False
        
        if 'ims_org_id' in resp.keys():
            return True
        else:
            logging.error(" ims_org_id for the - {} not present".format(aci_instance_id))
    except Exception:
        logging.error("Either wrong aci instance id provided or Error fetching instance details from aci")
   

def get_mkt_instance_id(aci_base_url,aci_instance_id,headers):
    try:
        """Get instance id from ACI."""
        url = aci_base_url + "connections?property=connected_instance==" + aci_instance_id
        res = requests.get(url, headers=headers)
        resp = json.loads(res.content)
        global con_type
        

        if resp['_page']['count'] >= 1:
            con_type = resp['results'][0]['connection_type']
            print(con_type)
            mkt_counter = 0
            data_counter = 0
            logging.info("multiple MKTs found for {} {} ACI ID, checking if all MKTs are active".format(con_type.upper(), aci_instance_id))
            for mkt_instance_counter in range(len(resp['results'])):
                mkt_data = resp['results'][mkt_instance_counter]
                mkt_data_con_type = resp['results'][mkt_instance_counter]['connection_check']['failed']
                if 'instance_id' in mkt_data.keys() and resp['results'][mkt_instance_counter] and mkt_data_con_type != True:
                    logging.info("MKT ACI instance_id {} <--> {} Instance id - {} & {} instance name - {} for counter {}".format(mkt_data['instance_id'], con_type.upper(), aci_instance_id, con_type.upper(), mkt_data['connected_instance_name'], mkt_instance_counter))
                    if _check_instance_exists(aci_base_url, mkt_data['instance_id'], headers):
                        mkt_counter = mkt_counter + 1
                        data_counter = mkt_instance_counter
                if mkt_data_con_type == True:
                   failed_reason=resp['results'][mkt_instance_counter]['connection_check']['reason']
                   logging.info("MKT ACI instance_id {} <--> {} Instance id - {} & {} instance name - {} failed due to {}".format(mkt_data['instance_id'], con_type.upper(), aci_instance_id, con_type, mkt_data['connected_instance_name'], failed_reason))

            if mkt_counter > 1:
                raise Exception("More than 1 match found for instance")
            if mkt_counter == 1:
                data = resp['results'][data_counter]
                if data['connection_type'] == 'mkt':   #if data['connection_type'] == 'mid' or
                    raise Exception("Exiting, as the ACI ID - {} provided is for mid or mkt instance type".format(aci_instance_id))
                elif data['connected_instance'] == aci_instance_id:
                    if 'instance_id' in data.keys():
                        logging.info("found MKT ACI instance_id {} <--> {} Instance id - {} & {} instance name - {}".format(data['instance_id'], con_type.upper(),aci_instance_id,con_type.upper(), data['connected_instance_name']))
                        return data['instance_id']
                    else:
                        raise Exception("MKT instance_id not found")
                else:
                    raise Exception("RT instance id - {} is different than found - {} in response".format(aci_instance_id, data['connected_instance']))
            if mkt_counter < 1:
                raise Exception("0 MKT instances are connected to RT")
        else:
            raise Exception("0 result fetched for provided instance, check if instance id is correct and is of rt instance")        
    except Exception as e:
        logging.error("Either wrong aci instance id provided or Error fetching mkt instance details from aci- {}".format(e))
        exit(1)

def get_instance_aci_details(aci_base_url,headers,aci_instance_id):
    try:
        """Get instance further details using aci_instance_id"""
        url = aci_base_url + "instances/" + aci_instance_id
        res = requests.get(url, headers=headers)
        resp = json.loads(res.content)
        #if all(key in resp.keys() dict for key in ("ims_org_id", "tenant_id")):
        if 'ims_org_id' in resp.keys():
            logging.info("({}) found IMS org id - {} ".format(resp['instance_name'], resp['ims_org_id']))
            if resp['instance_type'] == 'mkt':
                tenant_id = resp['tenant_id']
                return resp['ims_org_id'], tenant_id, resp['exc_tenant_id']
            else:
                return resp['ims_org_id'], resp['exc_tenant_id'], resp['instance_url'], resp['instance_type']
                
        else:
            logging.error("ims_org_id or tenant id missing.")
            raise Exception("ims_org_id")
    except Exception as e:
        logging.error("Error getting instance details from aci- {}".format(e))
        exit(1)

def verify_org_id(rt_org_id,mkt_org_id):
    try:
        if rt_org_id == mkt_org_id:
            logging.info("Fetched IMS Org ID for {} and MKT instances are same".format(con_type.upper()))
        else:
            logging.info("Fetched IMS Org ID for {} and MKT instances are not same".format(con_type.upper()))
            raise Exception
    except Exception as e:
        logging.error("Cannot proceed as IMS ORG ID of {} {} and MKT {} are not same- {}".format(con_type.upper(),rt_org_id, mkt_org_id, e))
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aci_id", type=str, help='ACI Instance ID', required=True)
    args = parser.parse_args()

    #token = retrieve_token()
    token = read_secret('ims_access_token')
    aci_base_url = "https://campaign-inventory-api.adobe.io/campaign/"
    headers = {"Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": "Bearer " + token,
                        "x-api-key": "campaign_ims_user_migration"
                        }
    
    aci_instance_id = args.aci_id
    mkt_aci_instance_id = get_mkt_instance_id(aci_base_url,aci_instance_id,headers)
    
    rt_org_id, rt_exc_tenant, rt_instance_url, rt_instance_type = get_instance_aci_details(aci_base_url,headers,aci_instance_id)
    print(rt_org_id, rt_exc_tenant, rt_instance_url, rt_instance_type)
    
    mkt_org_id, mkt_tenant_id, mkt_exc_tenant = get_instance_aci_details(aci_base_url,headers,mkt_aci_instance_id)
    print(mkt_org_id, mkt_tenant_id, mkt_exc_tenant)
    verify_org_id(rt_org_id,mkt_org_id)
    result = {"mkt_org_id": mkt_org_id, "mkt_tenant_id": mkt_tenant_id, "mkt_aci_instance_id": mkt_aci_instance_id, "mkt_exc_tenant": mkt_exc_tenant,  con_type + "_org_id": rt_org_id, con_type + "_exc_tenant": rt_exc_tenant, con_type + "_instance_url": rt_instance_url, con_type + "_instance_type": rt_instance_type}
    logging.info("after generating result")
    return json.dumps(result)
    

if __name__ == "__main__":
    print(main())
    