#!/usr/bin/env python3

import configparser
import pexpect
import argparse
import asyncio

async def update_password(host, old_pw, new_pw):
    print(f"Connecting to {host}...")
    connection = pexpect.spawn(f"ssh ubuntu@{host}", encoding="UTF-8")
    resp = await connection.expect(["\(yes/no\)\?", "password:", pexpect.TIMEOUT], async_=True)
    if resp == 2:
        print(f"Could not connect to host {host}")
        return
    elif resp == 0:
        print(f"adding host fingerprint for {host}...")
        connection.sendline("yes")
        await conn.expect(["password:"], async_=True)
        connection.sendline(old_pw)
    elif resp == 1:
        connection.sendline(old_pw)
    resp = await connection.expect(["Current password:", "Permission denied"], async_=True)
    if resp == 1:
        print(f"Incorrect password for host {host}. already updated?")
        return
    await send_updates(connection, old_pw, new_pw)
    print(f"Successfully updated password for host {host}")

async def send_password(conn, pw):
    conn.sendline(pw)

async def send_updates(conn, old_pw, new_pw):
    conn.sendline(old_pw)
    await conn.expect(["New password:"], async_=True)
    conn.sendline(new_pw)
    await conn.expect(["Retype new password:"], async_=True)
    conn.sendline(new_pw)

def get_hosts_from_ini(filename):
    host_conf = configparser.ConfigParser()
    host_conf.read(filename)
    return list(host_conf['servers'].values())

async def main():
    args_parser = argparse.ArgumentParser(description="Update passwords on hosts after base ubuntu install")
    args_parser.add_argument("--hosts_file")
    args_parser.add_argument("--hosts")
    args_parser.add_argument("--old_pw", default="ubuntu")
    args_parser.add_argument("--new_pw", default="oMKVrzZB5acvCQCsZUXk")
    args = args_parser.parse_args()
    hosts_file = args.hosts_file

    if args.hosts_file is not None:
        all_hosts = get_hosts_from_ini(args.hosts_file)
    elif args.hosts is not None:
        all_hosts = args.hosts.split(",")
    else:
        raise Exception("need to provide hosts")
    print(f"executing for hosts: {all_hosts}")
    tasks = [update_password(host, args.old_pw, args.new_pw) for host in all_hosts]
    await asyncio.gather(*tasks)
    print("Updated passwords on all hosts")

if __name__ == "__main__":
    asyncio.run(main())
