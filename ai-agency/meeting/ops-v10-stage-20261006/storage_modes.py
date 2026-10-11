"""Preserve private modes and narrowly shared case files across web/Hermes identities."""
import os,stat

def protect(path,kind='file'):
    if os.name!='posix':return
    import grp
    s=path.stat()
    shared=grp.getgrgid(s.st_gid).gr_name=='omnisense-client-data'
    mode=(0o2770 if shared else 0o700) if kind=='directory' else ((0o640 if kind=='key' else 0o660) if shared else 0o600)
    if s.st_uid==os.geteuid():path.chmod(mode)
    elif stat.S_IMODE(s.st_mode)!=mode:raise PermissionError('Private storage permissions mismatch')
