# CheckPing
The ping_test script can test multiple devices at once and confirm if the networking device is on state or not.
To run the script follow the below mentioned rules -

1. Create a dev_to_check.txt file and mention all the IPs in the file.
2. Select a server that is mentioned in the list.(Need to manually provide the server)
3. After choosing the server provide the login credentials.
4. If the login is successful, the script will automatically send 10 ICMP packets to each IP in the list and print the results in a excel file.
