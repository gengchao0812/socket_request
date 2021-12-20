# coding:utf-8

import socket
import json
import logging
from logging import handlers

from multiprocessing import Process
import re


class HTTPServer(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射
    form_list = ["Content-Type: application/x-www-form-urlencoded", "Content-Type: multipart/form-data"]
    json_list = ["Content-Type: application/json"]
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



    def start(self):
        self.server_socket.listen(128)
        while True:
            client_socket, client_address = self.server_socket.accept()
            print("[%s, %s]用户连接上了" % client_address)
            handle_client_process = Process(target=self.handle_client, args=(client_socket,))
            handle_client_process.start()
            client_socket.close()


    #请求类型返回到body
    def reponse_choice_content_type(self, request_all,response_body_tmp):
        if 'Content-Type: application/json' in request_all:
            response_body_tmp['Content - Type'] = 'application/json'
        elif 'Content-Type: application/xml' in request_all:
            response_body_tmp['Content - Type'] = 'application/xml'
        elif 'Content-Type: text/html' in request_all:
            response_body_tmp['Content - Type'] = 'text/html'
        elif 'Content-Type: text/plain' in request_all:
            response_body_tmp['Content - Type'] = 'text/plain'
        elif 'Content-Type: application/javascript' in request_all:
            response_body_tmp['Content - Type'] = 'application/javascript'
        elif 'Content-Type: application/x-www-form-urlencoded' in request_all:
            response_body_tmp['Content - Type'] = 'application/x-www-form-urlencoded'
        # elif 'Content-Type: multipart/form-data' in request_all:
        #     # response_headers = "content-type: multipart/form-data\r\n"
        #     response_body_tmp['Content - Type'] = 'multipart/form-data'
        else:
            response_body_tmp['Content - Type'] = 'multipart/form-data'

        return response_body_tmp


    #解析上送body的json
    def list_to_dict(self,list):
        #转字典
        list1 = []
        list2 = []
        for i in range(len(list)):
            list1.append(list[i].split("=")[0])
            list2.append(list[i].split("=")[1])
        dict_new = dict(zip(list1, list2))
        return dict_new

    def reponse_body_data(self,request_all,data_tmp):
        if request_all[-1] != "":
            data_tmp = request_all[-1].split("&")
            data_tmp = self.list_to_dict(data_tmp)
        else:
            data_tmp = ""
        return data_tmp

    def handle_client(self, client_socket):
        """
        处理客户端请求
        """
        # 获取客户端请求数据
        request_data = client_socket.recv(1024)
        print("request data:", request_data)
        request_lines = request_data.splitlines()
        print(request_lines)
        # 在 Python3 中，bytes 和 str 的互相转换方式是str.encode('utf-8') bytes.decode('utf-8')
        # byte 转str
        request_all_tmp = []
        for line in request_lines:
            request_all_tmp.append(line.decode("utf-8"))
        # 拆协议头，重新组装list，新list为request_all
        request_all = request_all_tmp[0].split(' ')
        for i in range(len(request_all_tmp)):
            if i == 0:
                pass
            else:
                request_all.append(request_all_tmp[i])
        print("request_all的值是：")
        print(request_all)
        # 条件取params和url,params是list
        #按照关键字b'', b第一个出现的位置做切分，后面的数据做切分
        #或者/r/n/r/n
        if "?" in request_all[1]:
            # url = request_all[1].split("?")[0]
            #按照？切分，取第二个值
            params_tmp = request_all[1].split("?")[1]
            params = params_tmp.split("&")
            params = self.list_to_dict(params)
        else:
            params = ""
            # url = request_all[1]
        #取data数据
        #定位data开始位置
        for i in range(len(request_all)):
            if 'Content-Length' in request_all[i]:
                print(i)
                print("gengnihaodfkasjdfasdfsadf")
                data_num = i+2
        data_tmp = []
        #放入列表
        for i in range(len(request_all)):
            if i >=data_num:
                data_tmp.append(request_all[i])
        # 取data数据，如果是form-urlencoded，利用json 把请求体切片拆掉
        # 注意返回的数据是list
        for i in range(len(self.form_list)):
            if self.form_list[i] in request_all:
                data_tmp = self.reponse_body_data(request_all, data_tmp)
        # 取ip
        ip = "127.0.0.1:8000"
        response_start_line = "HTTP/1.1 200 OK\r\n"
        #params 和data转字典传回来
        response_body_tmp = dict(method=request_all[0], url='http://'+ip+request_all[1], params=params, data=data_tmp)
        print("request_all值是：")
        print(request_all)
        response_body_tmp = self.reponse_choice_content_type(request_all,response_body_tmp)
        response_body = json.dumps(response_body_tmp)
        # response_headers = "socket : test\r\n"
        response_headers = "Server: My server\r\n"
        response = response_start_line + response_headers + "\r\n" + response_body
        print("response data:", response)
        # 向客户端返回响应数据
        client_socket.send(response.encode("UTF-8"))
        # 关闭客户端连接
        client_socket.close()

    def bind(self, port):
        self.server_socket.bind(("", port))


def main():
    http_server = HTTPServer()
    #服务器绑定到指定端口
    http_server.bind(8001)
    http_server.start()


if __name__ == "__main__":
    main()
