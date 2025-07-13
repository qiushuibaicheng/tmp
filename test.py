import paramiko
import os
from tqdm import tqdm

def check_remote_file_exists(sftp, remote_path):
    """查看远程文件是否存在"""
    try:
        sftp.stat(remote_path) # 查看文件是否存在
        return True
    except IOError:
        return False

def ensure_remote_directory_exists(sftp, remote_dir):
    """递归创建远程目录（如果不存在）"""
    dirs = remote_dir.split('/')
    current_path = ''
    for dir in dirs:
        if not dir:
            continue
        current_path += f"/{dir}"
        try:
            sftp.stat(current_path) # 查看文件夹是否存在
        except FileNotFoundError:
            sftp.mkdir(current_path)

def ssh_scp_transfer():
    # 服务器连接信息
    hostname = '192.168.142.130'
    port = 22  # 默认SSH端口
    username = 'luojing'
    password = ''  # 建议使用密钥认证更安全
    private_key_path = 'C:/Users/luojing/.ssh/id_rsa' # 可选，如果使用密钥认证

    # 本地和远程路径
    local_path = './config.json'
    remote_path = '/home/luojing/test/test/'
    remote_file_path = '/home/luojing/test/test/config.json'

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if os.path.exists(private_key_path):
                private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
                ssh.connect(hostname, port, username, pkey=private_key)
                print("使用密钥登录ssh成功")
        except Exception as e:
            print(f"使用密钥登陆失败， {e}")
            ssh.connect(hostname, port, username, password)
            print("使用密码登录ssh成功")
        # else:
        #     ssh.connect(hostname, port, username, password)
        #     print("使用密码登录ssh成功")

        sftp = ssh.open_sftp()

        # 获取本地文件大小（用于进度条）
        file_size = os.path.getsize(local_path)

        if os.path.isfile(local_path):
            print("传输的是文件")
            remote_dir = os.path.dirname(remote_path)
            ensure_remote_directory_exists(sftp, remote_dir)

            if check_remote_file_exists(sftp, remote_file_path):
                print(f"警告: 远程文件 {remote_file_path} 已存在，将被覆盖")
            # sftp.put(local_path, remote_file_path)
            # print(f"文件 {local_path} 传输完成")

            # 使用回调函数更新进度条
            with tqdm(
                    total=file_size,
                    unit='B',
                    unit_scale=True,
                    desc=f"上传 {os.path.basename(local_path)}"
            ) as pbar:
                def callback(uploaded_bytes, total_bytes):
                    pbar.update(uploaded_bytes - pbar.n)  # 更新进度

                sftp.put(local_path, remote_file_path, callback=callback)

            print(f"文件 {local_path} 传输完成")

        # elif os.path.isdir(local_path):
        #     print("传输的是文件夹")
        #     ensure_remote_directory_exists(sftp, remote_path)
        #
        #     for root, dirs, files in os.walk(local_path):
        #         relative_path = os.path.relpath(root, local_path)
        #         remote_dir_path = os.path.join(remote_path, relative_path)
        #
        #         try:
        #             sftp.stat(remote_dir_path)
        #         except IOError:
        #             sftp.mkdir(remote_dir_path)
        #             print(f"创建子目录: {remote_dir_path}")
        #
        #         for file in files:
        #             local_file = os.path.join(root, file)
        #             remote_file = os.path.join(remote_dir_path, file)
        #
        #             if check_remote_file_exists(sftp, remote_file):
        #                 print(f"警告: 远程文件 {remote_file} 已存在，将被覆盖")
        #             sftp.put(local_file, remote_file)
        #             print(f"文件 {file} 传输完成")

        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"传输过程中出现错误: {e}")

if __name__ == "__main__":
    ssh_scp_transfer()