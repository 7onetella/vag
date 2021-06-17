import time
import sys
import os

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester
                  
jenkins_url = "https://jenkins.7onetella.net/"

def run_job(job_name: str, params: dict):
    jenkins_api_token = os.getenv('JENKINS_API_TOKEN')

    crumb=CrumbRequester(username='admin', password=jenkins_api_token, baseurl=jenkins_url)

    jenkins = Jenkins(jenkins_url, username='admin', password=jenkins_api_token, requester=crumb, timeout=60)

    jenkins.build_job(job_name, params)

    job = jenkins[job_name]
    qi = job.invoke(build_params=params)

    tries = 0
    while not qi.is_queued():
      if tries > 10:
        break
      time.sleep(1)
      tries += 1

    if qi.is_queued() or qi.is_running():
      qi.block_until_complete(delay=3)

    build = qi.get_build()

    while build.is_running():
      print('.')
      time.sleep(5)

    is_build_good = build.is_good()

    if is_build_good is not True:
      print("build faild")
      print(build.get_console())
      sys.exit(1)

    if is_build_good is True:
      print(job_name + " is successful")      

