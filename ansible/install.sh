#!/bin/bash
# if [ $# -eq 0 ]; then
#     echo "You must provide the IP or hostname of the Raspberry Pi to configure."
#     exit 1
# fi
# ansible-playbook install.yml --ask-pass -u pi -i $1,

if [ $# -eq 0 ]; then
    ansible-playbook -vv -i labdash_hosts.yaml labdash_playbook.yml
else
    ## As is not possible to directly loop over the files in a directory with ansible, we need to first get the list of files and then loop over it in the next step. The "ls --format=comma -d ..." command lists the .epd files in the internals directory and formats them as a comma-separated list, which is then registered in the internal_jobs variable. The same applies for the themes.
    INTERNALS_JOBS=$(ls --format=comma -d $1/*.epd | tr -d \\n)
    INTERNALS_THEMES=$(ls --format=comma -d $1/themes/* | tr -d \\n)

    ansible-playbook -vv -i labdash_hosts.yaml labdash_playbook.yml --extra-vars "internal_jobs='$INTERNALS_JOBS' internal_themes='$INTERNALS_THEMES'"
fi

