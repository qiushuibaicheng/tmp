import json
import paramiko
import os

# 服务器连接信息
hostname = '192.168.142.130'
port = 22  # 默认SSH端口
username = 'luojing'
password = ''  # 建议使用密钥认证更安全
private_key_path = 'C:\\Users\\luojing\\.ssh\\id_rsa'  # 可选，如果使用密钥认证

# 本地和远程路径
local_path = './config.json'
remote_path = '/home/luojing/test/test/'
remote_file_path = '/home/luojing/test/test/config.json'


def main():
    with open("config.json", encoding="utf-8") as file_read:
        config: dict = json.loads(file_read.read())

    print(f"Hello from cmc! {config["test"]}")
    input("按Enter键退出...")


def ssh_scp_transfer():
    try:
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接服务器（密码或密钥认证）
        try:
            if os.path.exists(private_key_path):
                private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
                ssh.connect(hostname, port, username, pkey=private_key)
                print("使用密钥登录ssh成功")
        except Exception as e:
            print(f"使用密钥登陆失败， {e}")
            ssh.connect(hostname, port, username, password)
            print("使用密码登录ssh成功")

        command = ""

        while command not in ["quit", "exit"]:
            command = input(">")

            try:
                # 1. 执行命令
                stdin, stdout, stderr = ssh.exec_command(command)

                # 2. 读取输出
                output = stdout.read().decode('utf-8')  # 标准输出
                error = stderr.read().decode('utf-8')  # 错误输出

                if output:
                    print(output.rstrip())
                if error:
                    print(f"\033[31m{error.rstrip()}\033[0m")

            except Exception as e:
                print(f"执行失败: {str(e)}")

        # # 使用SFTP传输文件
        # sftp = ssh.open_sftp()
        #
        # # 检查本地路径是文件还是目录
        # if os.path.isfile(local_file_path):
        #     # 传输单个文件
        #     sftp.put(local_file_path, remote_file_path)
        #     print(f"文件 {local_file_path} 已成功传输到 {remote_file_path}")
        # elif os.path.isdir(local_file_path):
        #     # 递归传输整个目录
        #     for root, dirs, files in os.walk(local_file_path):
        #         remote_dir = os.path.join(remote_file_path, os.path.relpath(root, local_file_path))
        #         try:
        #             sftp.mkdir(remote_dir)
        #         except IOError:
        #             pass  # 目录已存在
        #         for file in files:
        #             local_file = os.path.join(root, file)
        #             remote_file = os.path.join(remote_dir, file)
        #             sftp.put(local_file, remote_file)
        #             print(f"文件 {local_file} 已传输到 {remote_file}")
        #     print(f"目录 {local_file_path} 已成功传输到 {remote_file_path}")
        #
        # # 关闭连接
        # sftp.close()
        ssh.close()

    except Exception as e:
        print(f"传输过程中出现错误: {e}")


if __name__ == "__main__":
    ssh_scp_transfer()
