from pcapkit import extract

# with open('data\\VLP-32c_Single.pcap', 'rb' , 10000) as file:
#     packets = extract(file, verbose=True)
    

extract('data\\VLP-32c_Single.pcap', format='json')