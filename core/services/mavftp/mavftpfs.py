#!/usr/bin/env python

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from mavftp import FTPUser
from pymavlink import mavutil
import os

import errno
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn


class MAVFTP(LoggingMixIn, Operations):
    def __init__(self, mav):
        self.mav = mav
        self.files = {"/": {"st_mode": (0o40755), "st_size": 0}}
        self.ftp = FTPUser(mav)

    # def chmod(self, path, mode):
    #     return self.sftp.chmod(path, mode)

    # def chown(self, path, uid, gid):
    #     return self.sftp.chown(path, uid, gid)

    # def create(self, path, mode):
    #     f = self.sftp.open(path, 'w')
    #     f.chmod(mode)
    #     f.close()
    #     return 0

    # def destroy(self, path):
    #     self.sftp.close()
    #     self.client.close()

    def getattr(self, path, fh=None):
        if path in self.files:
            return self.files[path]
        else:
            parent_dir = ("/" + "/".join(path.split("/")[:-1])).replace("//", "/")
            print(f"cache miss, asking for {parent_dir}")
            self.readdir(parent_dir)
            if path not in self.files:
                return {}
            return self.files[path]

    def read(self, path, size, offset, fh):
        buf = self.ftp.read_sector(path, offset, size)
        return buf

    def readdir(self, path, fh=0):
        dir = self.ftp.list(path)
        if dir is None or len(dir) == 0:
            return []
        ret = {}
        for item in dir:
            if item["name"] == "." or item["name"] == "..":
                continue
            if not item["is_dir"]:
                new_item = {"st_mode": (0o100666), "st_size": item["size_b"]}
            else:
                new_item = {"st_mode": (0o40755), "st_size": 0}
            ret[item["name"]] = new_item
            new_path = path if path.endswith("/") else path + "/"
            self.files[new_path + item["name"]] = new_item
        self.files[path] = {"st_mode": (0o40755), "st_size": 0}
        return ret

    # Override methods that modify filesystem state to return read-only error
    def write(self, path, data, offset, fh):
        raise FuseOSError(errno.EROFS)

    def mkdir(self, path, mode):
        raise FuseOSError(errno.EROFS)

    def rmdir(self, path):
        raise FuseOSError(errno.EROFS)

    def unlink(self, path):
        raise FuseOSError(errno.EROFS)

    def rename(self, old, new):
        raise FuseOSError(errno.EROFS)

    def chmod(self, path, mode):
        raise FuseOSError(errno.EROFS)

    def chown(self, path, uid, gid):
        raise FuseOSError(errno.EROFS)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser(description="MAVLink FTP", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-m",
        "--mavlink",
        default="udpin:127.0.0.1:14555",
        help="MAVLink connection specifier",
    )
    parser.add_argument(
        "--mountpoint",
        help="Path to the mountpoint",
    )

    args = parser.parse_args()

    if not os.path.exists(args.mountpoint):
        os.makedirs(args.mountpoint)

    fuse = FUSE(
        # SFTP(args.host, username=args.login),
        MAVFTP(mavutil.mavlink_connection(args.mavlink)),
        args.mountpoint,
        foreground=True,
        nothreads=True,
        allow_other=True,
    )
