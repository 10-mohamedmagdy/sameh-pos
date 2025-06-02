# For STMicroelectronics printers (your vendor ID 0483)
arabic_escpos_sequence = b'\x1B\x74\x13'  # Common Arabic code page command

printer._raw(arabic_escpos_sequence)
printer.text("تجربة طباعة\n")
printer.cut()