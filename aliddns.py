from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
import requests
from urllib.request import urlopen
import json

ipv4_flag = 0  # 是否开启ipv4 ddns解析,1为开启，0为关闭
ipv6_flag = 1  # 是否开启ipv6 ddns解析,1为开启，0为关闭
accessKeyId = "accessKeyId"  # 将accessKeyId改成自己的accessKeyId
accessSecret = "accessSecret"  # 将accessSecret改成自己的accessSecret
domain = "zeruns.tech"  # 你的主域名
name_ipv4_list = ["blog"]  # 要进行ipv4 ddns解析的子域名
name_ipv6_list = ["www", "notify"]  # 要进行ipv6 ddns解析的子域名


client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')

def update(RecordId, RR, Type, Value):  # 修改域名解析记录
    from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(RecordId)
    request.set_RR(RR)
    request.set_Type(Type)
    request.set_Value(Value)
    response = client.do_action_with_exception(request)


def add(DomainName, RR, Type, Value):  # 添加新的域名解析记录
    from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(DomainName)
    request.set_RR(RR)  # https://blog.zeruns.tech
    request.set_Type(Type)
    request.set_Value(Value)    
    response = client.do_action_with_exception(request)

def processIpv4(ipv4, subDomain):
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain)
    request.set_SubDomain(subDomain + '.' + domain)
    request.set_Type("A")
    response = client.do_action_with_exception(request)  # 获取域名解析记录列表
    domain_list = json.loads(response)  # 将返回的JSON数据转化为Python能识别的

    if domain_list['TotalCount'] == 0:
        add(domain, subDomain, "A", ipv4)
        print(subDomain + " 新建域名解析成功")
    elif domain_list['TotalCount'] == 1:
        if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipv4.strip():
            update(domain_list['DomainRecords']['Record'][0]['RecordId'], subDomain, "A", ipv4)
            print(subDomain + " 修改域名解析成功")
        else:  # https://blog.zeruns.tech
            print(subDomain + " IPv4地址没变")
    elif domain_list['TotalCount'] > 1:
        from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
        request = DeleteSubDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(domain)  # https://blog.zeruns.tech
        request.set_RR(subDomain)
        request.set_Type("A") 
        response = client.do_action_with_exception(request)
        add(domain, subDomain, "A", ipv4)
        print(subDomain + " 修改域名解析成功")

def processIpv6(ipv6, subDomain):
    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain)
    request.set_SubDomain(subDomain + '.' + domain)
    request.set_Type("AAAA")
    response = client.do_action_with_exception(request)  # 获取域名解析记录列表
    domain_list = json.loads(response)  # 将返回的JSON数据转化为Python能识别的

    if domain_list['TotalCount'] == 0:
        add(domain, subDomain, "AAAA", ipv6)
        print(subDomain + " 新建域名解析成功")
    elif domain_list['TotalCount'] == 1:
        if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipv6.strip():
            update(domain_list['DomainRecords']['Record'][0]['RecordId'], subDomain, "AAAA", ipv6)
            print(subDomain + " 修改域名解析成功")
        else:  # https://blog.zeruns.tech
            print(subDomain + " IPv6地址没变")
    elif domain_list['TotalCount'] > 1:
        from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
        request = DeleteSubDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(domain)
        request.set_RR(subDomain)  # https://blog.zeruns.tech
        request.set_Type("AAAA") 
        response = client.do_action_with_exception(request)
        add(domain, subDomain, "AAAA", ipv6)
        print(subDomain + " 修改域名解析成功")

if ipv4_flag == 1:
    ip = urlopen('https://api-ipv4.ip.sb/ip').read()  # 使用IP.SB的接口获取ipv4地址
    ipv4 = str(ip, encoding='utf-8')
    print("获取到IPv4地址：%s" % ipv4)
    for subDomain in name_ipv4_list:
        processIpv4(ipv4, subDomain)

if ipv6_flag == 1:
    ip = urlopen('https://api-ipv6.ip.sb/ip').read()  # 使用IP.SB的接口获取ipv6地址
    ipv6 = str(ip, encoding='utf-8')
    print("获取到IPv6地址：%s" % ipv6)
    for subDomain in name_ipv6_list:
        processIpv6(ipv6, subDomain)
