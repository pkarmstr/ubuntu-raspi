import configparser
import pexpect
import argparse
import asyncio

async def update_password(host, old_pw, new_pw):
    connection = pexpect.spawn(f"ssh ubuntu@{host}", encoding="UTF-8")
    resp = await connection.expect(["(yes/no)?", "password:", pexpect.TIMEOUT], async_=True)
    if resp == 2:
        print(f"Could not connect to host {host}")
        return
    elif resp == 0:
        print(f"adding host fingerprint for {host}...")
        connection.sendline("yes")
    elif resp == 1:
        pass
    await send_password(connection, old_pw)
    await send_updates(connection, old_pw, new_pw)
    print(f"Successfully updated password for host {host}")

async def send_password(conn, pw):
    await conn.expect(["password:"], async_=True)
    conn.sendline(pw)

async def send_updates(conn, old_pw, new_pw):
    await conn.expect(["Current password:"], async_=True)
    conn.sendline(old_pw)
    await conn.expect(["New password:"], async_=True)
    conn.sendline(new_pw)
    await conn.expect(["Retype new password:"], async_=True)
    conn.sendline(new_pw)

async def main():
    args_parser = argparse.ArgumentParser(description="Update passwords on hosts")
    args_parser.add_argument("hosts_file")
    args_parser.add_argument("--old_pw", default="ubuntu")
    args_parser.add_argument("--new_pw", default="oMKVrzZB5acvCQCsZUXk")
    args = args_parser.parse_args()
    hosts_file = args.hosts_file

    host_conf = configparser.ConfigParser()
    host_conf.read(hosts_file)
    all_hosts = list(host_conf['servers'].values())
    print(f"executing for hosts: {all_hosts}")
    tasks = [update_password(host, args.old_pw, args.new_pw) for host in all_hosts]
    await asyncio.gather(*tasks)
    print("Updated passwords on all hosts")

if __name__ == "__main__":
    asyncio.run(main())
