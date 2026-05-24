from mirage_vkfs.ops.dify.grep import grep
from mirage_vkfs.ops.dify.read import read
from mirage_vkfs.ops.dify.readdir import readdir
from mirage_vkfs.ops.dify.search import search
from mirage_vkfs.ops.dify.stat import stat

OPS = [read, readdir, stat, grep, search]
