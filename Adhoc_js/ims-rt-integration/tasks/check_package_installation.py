import requests
import json
#from read_access_token import retrieve_token 
from utils.vault_helper import read_secret 
import logging
import argparse

logging.basicConfig(level=logging.INFO)


def verify_packages(aci_base_url,aci_instance_id,headers,mid_package_names,rt_mkt_package_names):
    try:
        """Get instance id from ACI."""
        url = aci_base_url + "instances/" + aci_instance_id + "/databaseconfigs?field=packages" 
        res = requests.get(url, headers=headers)
        resp = json.loads(res.content)
        target_namespace = "nms"

        if resp['_page']['count'] >= 1:
            data = resp['results'][0]['packages']
            print(data)
            
            mid_package_found = False
            for item in data:
                if (item['namespace'] == target_namespace and item['name'] == mid_package_names):
                        mid_package_found = True
                        break

            if mid_package_found:
                for item in data:
                    if item['namespace'] == target_namespace and item['name'] in rt_mkt_package_names:
                        raise Exception("MID execution package - {} is installed with {}".format(mid_package_names, item['name']))
            else:
                raise Exception("MID execution package - {} is not present.".format(mid_package_names))
            
            return "SUCCESS"
        else:
            raise Exception("More than 1 result found for instance")
    except Exception as e:
        logging.error("Packages check for midReceiver installed failed with error- {}".format(e))
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aci_id", type=str, help='ACI Instance ID', required=True)
    args = parser.parse_args()

    
    token = read_secret('ims_access_token')
    aci_base_url = "https://campaign-inventory-api.adobe.io/campaign/"
    headers = {"Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": "Bearer " + token,
                        "x-api-key": "campaign_ims_user_migration"
                        }
    
    aci_instance_id = args.aci_id
    if True:
        mid_package_names = "midReceiver"
        rt_mkt_package_names = ['messageCenterExec', 'midEmitter', 'interactionExec', 'messageCenterControl']
        return(verify_packages(aci_base_url,aci_instance_id,headers,mid_package_names,rt_mkt_package_names ))
    

if __name__ == "__main__":
    print(main())
