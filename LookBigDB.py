import pandas as pd

FILES_NAME = {'file_prefix': f'BigData/bandwidth.csv',
              'file_data':   f'BigData/sample_big.csv',
              'file_result': f'BigData/result.csv'}

CHUNK_SIZE = 10 # Need to change 10 to 1000000 or 10000000


dbprefix = pd.read_csv(FILES_NAME['file_prefix'], header=None, delimiter=' ', names=['b'])

verification_list = dbprefix['b'].tolist()
i = 0   # count of looking chunks
mode_write = 'w'

for chunk in pd.read_csv(FILES_NAME['file_data'], chunksize=CHUNK_SIZE,
                         header=None, names=['a', 'b']):

    print('viewed ', i * CHUNK_SIZE, end='')
    records_found = chunk[chunk['b'].isin(verification_list)]
    if records_found.empty:
        print(' no matches')

    else:
        records_found.to_csv(FILES_NAME['file_result'],
                             mode=mode_write, header=False, index=False)
        print(' records ', len(records_found))
        mode_write = 'a'
        
    i += 1

print('end')
