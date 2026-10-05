"""Small truthful bare TAPEFS fixtures, derived solely from DRAFT10 §§2–5."""
import struct
import zlib
from pathlib import Path
from oracle import UUID, minimum_blocks, P1_START, P1_BLOCKS

BLOCKS=minimum_blocks(9)  # four chunks, not the old erroneous 60-second label
def crc(data): return zlib.crc32(data)&0xffffffff

def sb():
    b=bytearray(512); b[:8]=b'TAPEFS\0\x01'
    struct.pack_into('<HHI',b,8,1,0,1)
    b[20:36]=UUID
    struct.pack_into('<IHHIIII',b,36,44100,2,16,524288,9,4,1)
    struct.pack_into('<IIIIIII',b,60,65536,8,136,264,392,2048,BLOCKS-1)
    b[88:92]=b'WP14'
    struct.pack_into('<I',b,120,315532800)
    struct.pack_into('<I',b,508,crc(b[:508]))
    return b

def index(side,sequence):
    e=struct.pack('<III',0,0,128)
    h=bytearray(512); h[:8]=b'TAPEIDX\x01'
    struct.pack_into('<I',h,8,sequence); h[12]=side
    struct.pack_into('<IQ',h,16,1,128)
    struct.pack_into('<I',h,60,crc(h[:60]+e))
    return h,e.ljust(512,b'\0')

def build(path,mutation='clean'):
    blocks={0:sb(),BLOCKS-1:sb(),2048:bytes((i*17+3)&255 for i in range(512))}
    for side,base in ((0,8),(1,264)):
        h,e=index(side,side+1); blocks[base]=h; blocks[base+1]=e
    if mutation=='torn-primary': blocks[0][32]^=1
    elif mutation=='both-superblocks-bad':
        blocks[0][32]^=1; blocks[BLOCKS-1][32]^=1
    elif mutation=='flipped-a-entry':
        e=bytearray(blocks[9]); e[0]^=1; blocks[9]=e
    elif mutation=='degraded-b': blocks[264]=bytes(512)
    elif mutation=='invalid-standby': blocks[136]=b'corrupt standby'.ljust(512,b'\0')
    elif mutation!='clean': raise ValueError(mutation)
    with Path(path).open('wb') as f:
        f.truncate(BLOCKS*512)
        for lba,data in blocks.items(): f.seek(lba*512); f.write(data)
    return blocks

def synthetic_fat(path, fat_sectors=32):
    """A legal alternate FAT allocation for testing the reader, never Product bytes."""
    boot=bytearray(512); boot[:3]=b'\xeb\x3c\x90'; boot[3:11]=b'VERIFIER'
    struct.pack_into('<H',boot,11,512)
    struct.pack_into('<BHBHHBH',boot,13,4,1,2,512,P1_BLOCKS,0xf8,fat_sectors)
    struct.pack_into('<HHI',boot,24,63,255,P1_START)
    boot[36]=0x80; boot[38]=0x29; boot[43:54]=b'DIGITALTAPE'
    boot[54:62]=b'FAT16   '; boot[510:512]=b'\x55\xaa'
    readme=(b'This is a Digital Tape cartridge.\r\nLabel: WP14\r\n'
            b'Please do not format or erase this card on a computer.\r\n'
            b'Use the Digital Tape app to load music onto it.\r\n')
    fat=bytearray(fat_sectors*512); struct.pack_into('<HHH',fat,0,0xfff8,0xffff,0xffff)
    root=bytearray(16384); root[:11]=b'README  TXT'; root[11]=0x20
    struct.pack_into('<H',root,26,2); struct.pack_into('<I',root,28,len(readme))
    with Path(path).open('wb') as f:
        f.truncate((P1_START+P1_BLOCKS)*512)
        f.seek(P1_START*512); f.write(boot)
        f.seek((P1_START+1)*512); f.write(fat); f.write(fat); f.write(root)
        f.write(readme)
