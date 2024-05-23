#!/usr/bin/env python

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from mavftp import FTPUser
from pymavlink import mavutil
import os
import time
from loguru import logger

import errno
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn


class MAVFTP(LoggingMixIn, Operations):
    def __init__(self, mav):
        self.mav = mav
        self.files = {
            "/": {
                "st_mode": 0o40755,   # Directory with rwxr-xr-x permissions
                "st_nlink": 2,        # Self-link and parent link
                "st_size": 0,         # Size 0 for simplicity
                "st_ctime": time.time(),  # Current time
                "st_mtime": time.time(),  # Current time
                "st_atime": time.time(),  # Current time
                # "st_uid": os.getuid(),    # Owner's user ID
                # "st_gid": os.getgid()     # Owner's group ID
            }
        }
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
        logger.info(f"Fuse: getattr {path}")
        if path in self.files:
            return self.files[path]
        else:
            parent_dir = ("/" + "/".join(path.split("/")[:-1])).replace("//", "/")
            logger.debug(f"cache miss, asking for {parent_dir}")
            self.readdir(parent_dir)
            if path not in self.files:
                raise FuseOSError(errno.ENOENT)
            return self.files[path]

    def read(self, path, size, offset, fh):
        buf = self.ftp.read_sector(path, offset, size)
        #logger.info(f"read result: {buf}")
        return buf

    def readdir(self, path, fh=0):
        logger.info(f"Fuse: readdir {path}")  
        dir = self.ftp.list(path)
        if dir is None or len(dir) == 0:
            return []
        ret = {}
        for item in dir:
            if item["name"] == "." or item["name"] == "..":
                continue
            if not item["is_dir"]:
                new_item = {"st_mode": (0o100444), "st_size": item["size_b"]}
            else:
                new_item = {
                  "st_mode": (0o46766),                 
                  "st_nlink": 2,        # Self-link and parent link
                  "st_size": 0,         # Size 0 for simplicity
                  "st_ctime": time.time(),  # Current time
                  "st_mtime": time.time(),  # Current time
                  "st_atime": time.time(),  # Current time
                }
            ret[item["name"]] = new_item
            new_path = path if path.endswith("/") else path + "/"
            self.files[new_path + item["name"]] = new_item
        self.files[path] = {"st_mode": (0o46766), "st_size": 0}
        return ret

    # Override methods that modify filesystem state to return read-only error

    def ensure_file_exists(self, path):
        logger.info(f"making sure {path} exists...")
        try:
            self.getattr(path)
        except FuseOSError as e:
            logger.info(f"{path} didn't exist({e}). creating it...")
            self.create(path)

    
    def create(self, path, fi=None):
        '''
        When raw_fi is False (default case), fi is None and create should
        return a numerical file handle.

        When raw_fi is True the file handle should be set directly by create
        and return 0.
        '''
        logger.info(f"Fuse: create {path}, fi={fi}")
        self.ftp.create_file(path)
        logger.info(f"Fuse: created")
        return 0


    def mknod(self, path):
        logger.error(f"Fuse: lookup {path}")
        raise FuseOSError(errno.ENOENT)

    def write(self, path, data, offset, fh):
        self.ensure_file_exists(path)
        self.ftp.open_wo(path)
        logger.info(f"Fuse: write {path}, offset={offset}, fh={fh}, data={len(data)}")
        return self.ftp.write_file(path, offset, data, fh)


    def mkdir(self, path, mode):
        logger.error(f"Fuse: mkdir {path}")
        raise FuseOSError(errno.EROFS)

    def rmdir(self, path):
        logger.error(f"Fuse: rmdir {path}")
        raise FuseOSError(errno.EROFS)

    def unlink(self, path):
        logger.error(f"Fuse: unlink {path}")
        raise FuseOSError(errno.EROFS)

    def rename(self, old, new):
        logger.error(f"Fuse: rename {old} -> {new}")
        raise FuseOSError(errno.EROFS)

    def chmod(self, path, mode):
        logger.error(f"Fuse: chmod {path}")
        raise FuseOSError(errno.EROFS)

    def chown(self, path, uid, gid):
        logger.error(f"Fuse: chown {path}")
        raise FuseOSError(errno.EROFS)

    def truncate(self, path, other):
        logger.info(f"Fuse: truncate {path}")
        return self.create(path)

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
        ro=False,
        nothreads=True,
        allow_other=True,
        #debug=True,
    )
