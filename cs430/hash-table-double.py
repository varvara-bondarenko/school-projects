A = [32, 65, 98, 66, 26, 37, 38, 69, 73, 77, 14, 61, 90, 93, 31]


def hash_table_double(A):
    hash_table = {}
    
    for key in A:
        h1 = (2 * key + 5) % 17
        
        if h1 not in hash_table.keys():
            hash_table[h1] = key
        else:
            h2 = 7 - (key % 7)
            
            i = 1
            while True:
                func = (h1 + i * h2) % 17
                
                if func not in hash_table.keys():
                    hash_table[func] = key
                    break
                
                i += 1
        
        print(hash_table)
    
    hash_table = dict(sorted(hash_table.items()))
    print("final hash table: ", hash_table)
        
__main__ = hash_table_double(A)