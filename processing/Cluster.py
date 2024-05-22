import pandas as pd
import glob
import os
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

def cluster(path):
    all_files = sorted(glob.glob(os.path.join(path, '*.csv')),key=os.path.getmtime)
    parent_directory = os.path.dirname(path)
    if not os.path.exists(parent_directory + '\Cluster'):
        os.makedirs(parent_directory + '\Cluster')
    distance_threshold = 0.5
    min_data_points = 15

    for frame, filename in enumerate(all_files):
        df = pd.read_csv(filename, index_col=None)
        distances = pdist(df[['Points_m_XYZ:0','Points_m_XYZ:1']], metric='euclidean')
        linked = linkage(distances, method='single')
        cluster_ids = fcluster(linked, t=distance_threshold, criterion='distance')
        df['cluster_id'] = cluster_ids
        cluster_sizes = df['cluster_id'].value_counts()
        valid_clusters = cluster_sizes[cluster_sizes >= min_data_points].index
        # Filter the data to keep only the valid clusters
        df = df[df['cluster_id'].isin(valid_clusters)]
        df.to_csv(parent_directory+'\Cluster\clusterR' + str(frame) + '.csv', index=False)
    return parent_directory+'\Cluster'

