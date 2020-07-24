#!/bin/bash

# colors
red="\e[1;31m"
blue="\e[1;34m"
no_color="\e[0m"

# function to display errors in RED color
displayError() {
    error=$1
    echo -e -n $red
    echo -n \-\>$error
    echo -e $no_color
}

# exit function for erroneous executions
exitFunc() {
    exit_code=$1
    if [ $exit_code -ne 0 ]; then
        displayError "Error occured :("
    fi
    exit $exit_code
}

# initial variables checking
exit_code=0
if [ -z "$nas_aws_profile" ]; then
    displayError "nas_aws_profile - not set!"
    exit_code=1
fi
if [ -z "$nas_aws_region" ]; then
    displayError "nas_aws_region - not set!"
    exit_code=1
fi
if [ -z "$nas_keyvalue" ]; then
    displayError "nas_keyvalue - not set!"
    exit_code=1
fi
if [ -z "$nas_logstash_username" ]; then
    displayError "nas_logstash_username - not set!"
    exit_code=1
fi
if [ -z "$nas_logstash_password" ]; then
    displayError "nas_logstash_password - not set!"
    exit_code=1
fi
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

# set AWS Profile to the one inputted
export AWS_PROFILE=$nas_aws_profile
# set AWS Region
export AWS_REGION=$nas_aws_region

# activation of cco_lmsgw_v12 nodeenv
nodeenv_dir=~/node_env/cco_lmsgw_v12
if [ ! -d $nodeenv_dir ]; then
    displayError "nodeenv - not set up! Please create cco_lmsgw nodeenv."
    exit 1
fi
echo -e $blue\===Activating nodeenv===$no_color
. .$nodeenv_dir/bin/activate

# Check node version
node -v

echo "cco_lmsgw_v12 nodeenv activated!"

# deployment of NAS Agent Lambda GW
echo -e $blue\===NAS Agent Deployment===$no_color
if [ "$dep_nas" = true ]; then
    cd nas-agent-lambda-gw/nas-agent-deployment
    if [ "$create_domain" = true ]; then
        # create custom domain
        sls create_domain || exitFunc $?
    fi
    # deploy component
    sls deploy || exitFunc $?
else
    echo "Skipped"
fi

# deactivation of nodeenv
deactivate_node
