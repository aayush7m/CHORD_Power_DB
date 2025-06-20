import spidev
import time
import config
from typing import List
from flask import jsonify
import utilities
import threading
import queue
from config import Ansi

spi = spidev.SpiDev()
spi_lock = threading.Lock()
command_queue = queue.Queue()

def _spi_worker():
    while True:
        command_batch, resp_evt, resp_container = command_queue.get()
        latest_result = None
        ct = 0
        try:
            with spi_lock:
                print("doing the commands now")
                for cmd in command_batch:
                    ct += 1
                    print(f"cur cmd list is {cmd.cmd_list}")
                    latest_result = spi.xfer2(cmd.cmd_list)
    
        except Exception as e:
            print(f"{Ansi.BOLD}{Ansi.ITALIC}{Ansi.RED}"
                  f"SPI Transaction failed w/ Exception: {e}"
                  f"{Ansi.RESET}")
            print(f"{Ansi.BOLD}{Ansi.UNDERLINE}{Ansi.ITALIC}{Ansi.RED}"
                  f"[ERROR]{Ansi.RESET} "
                  f"{Ansi.BOLD}SPI transaction failed at batch index {ct}!{Ansi.RESET}")
            print(f"{Ansi.BOLD}{Ansi.ITALIC}{Ansi.YELLOW}"
                  "Batch command descriptions:"
                  f"{Ansi.RESET}")
            for i, c in enumerate(command_batch):
                print(f"  {Ansi.BOLD}[{i}]{Ansi.RESET} {getattr(c, 'text_cmd_list', c)}")


        resp_container['result'] = latest_result
        resp_evt.set()

def setup_spi(bus=None, device=None, speed_hz=config.speed_hz, mode=config.mode):
    """Setup SPI connection"""
    bus = bus if bus is not None else config.spi_bus
    device = device if device is not None else config.spi_device
    
    try:
        print(f"Setting up SPI on bus {bus}, device {device}")
        spi.open(bus, device)
        spi.max_speed_hz = speed_hz
        spi.mode = mode 
        print(f"SPI setup complete. Speed: {spi.max_speed_hz}Hz, Mode: {spi.mode}")
        # Start worker thread
        threading.Thread(target=_spi_worker, daemon=True).start()
        return True
    except Exception as e:
        print(f"SPI setup failed: {e}")
        return False

def close_spi():
    """Close SPI connection"""
    try:
        # Check if spi is open by checking if fd attribute exists and is a valid file descriptor
        if hasattr(spi, 'fd') and isinstance(spi.fd, int) and spi.fd > 0:
            spi.close()
            print("SPI bus closed.")
        else:
            print("SPI bus was not open.")
    except Exception as e:
        print(f"Error closing SPI: {e}")

class Operation:
    def __init__(self, read=None, write=None):
        self.read_reg = read
        self.write_reg = write

    def read(self):
        if self.read_reg is not None:
            return self.read_reg
        else:
            print("Cannot read from this operation")
        return []

    def write(self):
        if self.write_reg is not None:
            return self.write_reg
        else:
            print("Cannot write to this operation")
        return []
    
    def can_write(self):
        return self.write_reg is not None
    
    def can_read(self):
        return self.read_reg is not None


# TLE75080 chip in a daisy chain. many boards where each board has two chips (a,b)
operations = { # read, write
    'OUT': Operation([0x40,0x02], [0x80]), # output voltage
    'DIAG_OLON': Operation([0x4A,0x02], None), # results of open load check
    'DIAG_OLONEN': Operation([0x4B,0x02], [0x8B]), # set/see the channel for open load check
    'HWCR_OCL': Operation([0x4D,0x02], [0x8D]), # output control latch
    'STD_DIAG': Operation([0x00,0x01], None),
}

def get_cmd (op, mode, param):
    cmd = []
    cur_op = operations[op]
    if mode == 'r':
        if cur_op.can_read():
            cmd += cur_op.read()
        else: 
            raise ValueError()
    if mode == 'w':
        if cur_op.can_write():
            cmd += cur_op.write()
        else: 
            raise ValueError()
    cmd += param if param is not None else []
    return cmd

class Command:
    def __init__(self, data=None, text=None):
        if data is None:
            self.cmd_list = operations['STD_DIAG'].read() * (2 * config.board_ct)
        else:
            self.cmd_list = data.copy()
        
        if text is None:
            self.text_cmd_list = [""] * (2*config.board_ct)
        else:
            self.text_cmd_list = text.copy() 
    
    def set_board_chip(self, board_idx, chip_letter, op, mode, param=None):
        """Set command for specific board and chip"""
        cmd = get_cmd(op, mode, param)
        
        chip_idx = 2 if chip_letter.lower() == 'a' else 0
        idx = len(self.cmd_list) - ((board_idx + 1) * 4) + chip_idx
            
        self.cmd_list[idx:idx+2] = cmd
        self.text_cmd_list[idx//2] = f"chip {board_idx}{chip_letter}: {op}{mode}" + (f" {param[0]}" if param is not None else "")

    def set_all_boards(self, op, mode, param):
        """Set same command for all boards"""
        cmd = get_cmd(op, mode, param)

        self.cmd_list = cmd * (2 * config.board_ct)

        for i in range (len(self.text_cmd_list)):
            board_idx = config.board_ct - (i // 2) - 1
            chip_idx = 'b' if i % 2 == 0 else 'a'
            self.text_cmd_list[i] = f"chip {board_idx}{chip_idx}: {op}{mode}" + (f" {param[0]}" if param is not None else "")
        
    def __str__(self):
        return f"{str(self.cmd_list)} and {str(self.text_cmd_list)}"
    def __repr__(self):
        return f"{str(self.cmd_list)} and {str(self.text_cmd_list)}"

# std_diag_var = Command()

def run (cmd_batch, w_resp=False):
    print("hi hello ")
    resp_evt = threading.Event()
    resp = {}
    if w_resp:
        std_diag_var = Command()
        cmd_batch.append(std_diag_var)
    
    command_queue.put((cmd_batch, resp_evt, resp))
    resp_evt.wait()
    return resp.get('result')

