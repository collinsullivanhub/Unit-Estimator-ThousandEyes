import json
import requests
import xlsxwriter
import datetime
import time


def get_account_groups():

    row = 0
    col = 0

    headers = {"content-type": "application/json"}
    result = requests.get(
        "https://api.thousandeyes.com/v6/account-groups.json",
        headers=headers,
        auth=(username, api_key)
    )
    query = result.json()['accountGroups']
    for ag in query:
        ag_name = ag['accountGroupName']
        ag_aid = ag['aid']
        print(ag_name + " " + str(ag_aid))
        ag_aid_list.append(ag_aid)
        ag_name_list.append(ag_name)
        cell_format = workbook.add_format()
        cell_format.set_pattern(1)
        cell_format.set_bg_color('#CCFFFF')
        worksheet.write(row, col, ag_name, cell_format)
        worksheet.write(row, col + 1, ag_aid)
        row += 1


def populate_excel():
    headers = {"content-type": "application/json"}
    for ag_name, aid in zip(ag_name_list, ag_aid_list):
        row = 0
        col = 0
        cell_format = workbook.add_format()
        cell_format.set_pattern(1)
        cell_format.set_bg_color('#CCFFFF')
        cell_format2 = workbook.add_format()
        cell_format2.set_pattern(1)
        cell_format2.set_bg_color('#99CCFF')
        sheet = workbook.add_worksheet(f'{aid}')
        sheet.write(row, col, f"{ag_name}", cell_format2)
        sheet.write(row, col + 1, "AG Aid", cell_format2)
        sheet.write(row, col + 2, "Test Name", cell_format2)
        sheet.write(row, col + 3, "Test Type", cell_format2)
        sheet.write(row, col + 4, "Test ID", cell_format2)
        sheet.write(row, col + 5, "Enabled", cell_format2)
        sheet.write(row, col + 6, "Interval", cell_format2)
        sheet.write(row, col + 7, "Agent Count", cell_format2)
        sheet.write(row, col + 8, "Total Calculation", cell_format2)
        result = requests.get(
            f"https://api.thousandeyes.com/v6/tests.json?aid={aid}",
            headers=headers,
            auth=(username, api_key)
        )
        query = result.json()['test']
        for x in query:
            try:
                testName = x['testName']
                testId = x['testId']
                type = x['type']
                enabled = x['enabled']
                interval = x['interval']
                print(f"[\u001b[32m[*]\u001b[0m Populating test data \u001b[33m{testId}\u001b[0m for Account Group: {aid}")
                sheet.write(row + 1, col, f"{ag_name}", cell_format)
                sheet.write(row + 1, col + 1, f"{aid}")
                sheet.write(row + 1, col + 2, f"{testName}", cell_format)
                sheet.write(row + 1, col + 3, f"{type}")
                sheet.write(row + 1, col + 4, f"{testId}", cell_format)
                sheet.write(row + 1, col + 5, f"{enabled}")
                sheet.write(row + 1, col + 6, f"{interval}", cell_format)
                agent_count = get_test_details(testId, aid)
                sheet.write(row + 1, col + 7, agent_count)
                if enabled == "0" or 0:
                    print('\u001b[31m[X] Currently disabled \u001b[0m- not calculating cost...')
                    pass
                if enabled == "1" or 1:
                    cost = calculate_cost(type, interval, agent_count, testId)
                    print('\u001b[32m[*] Cost for test: ' + str(cost))
                    sheet.write(row + 1, col + 8, cost)
                row += 1
            except:
                pass
            #time.sleep(1)


def get_test_details(testId, aid):
    headers = {"content-type": "application/json"}
    agent_count = 0
    test_details = requests.get(
        f"https://api.thousandeyes.com/v6/tests/{testId}.json?aid={aid}",
        headers=headers,
        auth=(username, api_key)
    )
    print(test_details)
    test_details_query = test_details.json()['test']
    for x in test_details_query:
        agent = x['agents']
        for y in agent:
            agent_count += 1
    return agent_count


def get_timeout_values_http_serv_transaction(testId, aid):
    headers = {"content-type": "application/json"}
    test_details = requests.get(
        f"https://api.thousandeyes.com/v6/tests/{testId}.json?aid={aid}",
        headers=headers,
        auth=(username, api_key)
    )
    print(f"[*] Getting timeout value for {testId}")
    print(test_details)
    query = test_details.json()['test']
    httpTimeLimit = query['httpTimeLimit']
    return httpTimeLimit


def get_timeout_values_load(testId, aid):
    headers = {"content-type": "application/json"}
    test_details = requests.get(
        f"https://api.thousandeyes.com/v6/tests/{testId}.json?aid={aid}",
        headers=headers,
        auth=(username, api_key)
    )
    print(f"[*] Getting timeout value for {testId}")
    print(test_details)
    query = test_details.json()['test']
    httpTimeLimit = query['httpTimeLimit']
    pageLoadTimeLimit = query['pageLoadTimeLimit']
    x = pageLoadTimeLimit - httpTimeLimit
    return x


def calculate_cost(type, interval, agent_count, testId):

    if interval == 60:
        interval = 1
    if interval == 150:
        interval = 2.5
    if interval == 300:
        interval = 5
    if interval == 600:
        interval = 10
    if interval == 1200:
        interval = 20
    if interval == 2400:
        interval = 40
    if interval == 3600:
        interval = 60

    '''
    agent-to-server
    agent-to-agent
    bgp
    http-server
    page-load
    transactions
    web-transactions
    ftp-server
    dns-trace
    dns-server
    dns-dnssec
    dnsp-domain
    dnsp-server
    sip-server
    voice (RTP Stream)
    '''
    #For testing
    #print("interval is: " + str(min_interval))

    if type == "agent-to-server":
        return(2.5 * (60/interval) * 24 * 31 * agent_count)
    if type == "dns-server":
        return("DNS TBD")
    if type == "voice":
        return("Voice TBD")
    if type == "agent-to-agent":
        return(2.5 * (60/interval) * 24 * 31 * agent_count)
    if type == "http-server":
        #timeout = get_timeout_values_http_serv_transaction(testId, aid)
        #httpTimeLimit
        return(5 * 0.5 * (60/interval) * 24 * 31 * agent_count)
    if type == "page-load":
        #httpTimeLimit
        #pageLoadTimeLimit
        #timeout = get_timeout_values_load(testId, aid)
        return(5 * (60/interval) * 24 * 31 * agent_count)
    if type == "web-transactions":
        #httpTimeLimit
        #timeout = get_timeout_values_http_serv_transaction(testId, aid)
        return(5 * 0.5 * (60/interval) * 24 * 31 * agent_count)
    else:
        pass


if __name__ == "__main__":

    workbook = xlsxwriter.Workbook('reporting.xlsx')
    worksheet = workbook.add_worksheet()
    ag_name_list =  []
    ag_aid_list = []

    username = ""
    api_key = ""

    get_account_groups()
    populate_excel()
    workbook.close()
