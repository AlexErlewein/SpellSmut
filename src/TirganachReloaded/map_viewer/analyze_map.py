import struct
import sys
import zlib

# File header: 20 bytes (magic, format, type, version, checksum)
# Chunk header: 12 bytes uncompressed, 16 bytes compressed
#   chunk_id (2), occ_id (2), is_compressed (2), data_length (4), data_type (2)
#   if compressed: uncompressed_length (4)

map_path = r'i:\Spellforce Platinum Edition\map\lanfreegame\Liannon_AL.map'

with open(map_path, 'rb') as f:
    # Read file header
    magic, fmt, typ, ver, checksum = struct.unpack('<iiiii', f.read(20))
    print(f"File header: magic={hex(magic)}, format={fmt}, type={typ}, version={ver}")
    
    chunks = []
    while f.tell() < f.seek(0, 2):  # get file size
        f.seek(f.tell() if chunks else 20)  # reset position
        break
    
    f.seek(20)  # after header
    
    while True:
        pos = f.tell()
        header_data = f.read(12)
        if len(header_data) < 12:
            break
        
        chunk_id, occ_id, is_compressed, data_length, data_type = struct.unpack('<hhHih', header_data)
        
        uncompressed_length = 0
        if is_compressed:
            extra = f.read(4)
            if len(extra) < 4:
                break
            uncompressed_length = struct.unpack('<i', extra)[0]
        
        # Read chunk data
        chunk_data = f.read(data_length)
        if len(chunk_data) < data_length:
            break
        
        # Decompress if needed
        if is_compressed and len(chunk_data) > 0:
            try:
                # Skip zlib header (78 9c) and decompress
                decompressed = zlib.decompress(chunk_data, 15)  # auto-detect header
                chunk_data = decompressed
            except Exception as e:
                print(f"  Decompression failed for chunk {chunk_id}: {e}")
        
        chunks.append({
            'pos': pos,
            'chunk_id': chunk_id,
            'occ_id': occ_id,
            'is_compressed': is_compressed,
            'data_length': data_length,
            'data_type': data_type,
            'uncompressed_length': uncompressed_length,
            'data': chunk_data
        })
    
    print(f'\nFound {len(chunks)} chunks')
    
    # Find chunk 42 (movement flags) and chunk 29 (objects)
    for c in chunks:
        if c['chunk_id'] in [29, 42, 56]:
            print(f"\nChunk {c['chunk_id']}: type={c['data_type']}, compressed={c['is_compressed']}, data_len={len(c['data'])}, pos={c['pos']}")
            
            data = c['data']
            
            if c['chunk_id'] == 42:
                # Movement flags - list of (x, y) coordinates
                num_flags = len(data) // 4
                print(f"  Movement flag count: {num_flags}")
                if num_flags > 0:
                    for i in range(min(num_flags, 20)):
                        x, y = struct.unpack('<hh', data[i*4:i*4+4])
                        print(f"    Flag {i}: ({x}, {y})")
            
            if c['chunk_id'] == 29:
                # Objects - depends on chunk type
                print(f"  Chunk data type: {c['data_type']}")
                if c['data_type'] == 6:
                    obj_size = 16  # 2+2+2+2+2+2+4 = 16 bytes
                elif c['data_type'] >= 7:
                    obj_size = 18  # 16 + 2 bytes for collision flags
                elif c['data_type'] == 5:
                    obj_size = 14
                elif c['data_type'] == 4:
                    obj_size = 12
                else:
                    obj_size = 10
                
                num_objects = len(data) // obj_size
                print(f"  Object count (approx): {num_objects}, obj_size={obj_size}")
                
                # Parse objects and find ones with block_movement
                offset = 0
                count = 0
                block_mov_objects = []
                while offset + obj_size <= len(data):
                    x, y, obj_id, angle, npc_id = struct.unpack('<hhhhH', data[offset:offset+10])
                    unk1 = 0
                    if c['data_type'] >= 4:
                        unk1 = struct.unpack('<H', data[offset+10:offset+12])[0]
                    
                    # Check if block_movement flag is in high bit of unk1
                    block_movement = (unk1 & 0x8000) != 0
                    unk1_clean = unk1 & 0x7FFF
                    
                    if block_movement:
                        block_mov_objects.append((x, y, obj_id, angle, npc_id, unk1_clean))
                    
                    if count < 5:
                        print(f"    Obj {count}: pos=({x},{y}), id={obj_id}, angle={angle}, npc={npc_id}, unk1={unk1_clean}, block_mov={block_movement}")
                    
                    offset += obj_size
                    count += 1
                
                print(f"  Total objects: {count}")
                if block_mov_objects:
                    print(f"  Objects with block_movement flag: {len(block_mov_objects)}")
                    for obj in block_mov_objects:
                        print(f"    pos=({obj[0]},{obj[1]}), id={obj[2]}, angle={obj[3]}")
                else:
                    print(f"  No objects with block_movement flag set")
    
    # Check if block_movement object positions are in chunk 42
    chunk42 = next((c for c in chunks if c['chunk_id'] == 42), None)
    chunk29 = next((c for c in chunks if c['chunk_id'] == 29), None)
    
    if chunk42 and chunk29:
        # Get all movement flag positions
        movement_flags = set()
        data42 = chunk42['data']
        for i in range(len(data42) // 4):
            x, y = struct.unpack('<hh', data42[i*4:i*4+4])
            movement_flags.add((x, y))
        
        print(f"\n=== Checking if block_movement objects are in chunk 42 ===")
        
        # Parse objects again
        data29 = chunk29['data']
        obj_size = 16 if chunk29['data_type'] == 6 else 18
        offset = 0
        while offset + obj_size <= len(data29):
            x, y, obj_id, angle, npc_id = struct.unpack('<hhhhH', data29[offset:offset+10])
            unk1 = struct.unpack('<H', data29[offset+10:offset+12])[0]
            block_movement = (unk1 & 0x8000) != 0
            
            if block_movement:
                in_chunk42 = (x, y) in movement_flags
                print(f"  Object at ({x},{y}) id={obj_id}: in chunk42={in_chunk42}")
                
                # Count how many tiles are blocked for this object
                nearby_in_chunk42 = []
                for dx in range(-5, 6):
                    for dy in range(-5, 6):
                        if (x+dx, y+dy) in movement_flags:
                            nearby_in_chunk42.append((x+dx, y+dy))
                print(f"    Tiles blocked within 5 tiles: {len(nearby_in_chunk42)}")
                if nearby_in_chunk42:
                    print(f"    Blocked tiles: {nearby_in_chunk42}")
            
            offset += obj_size
