# SZZ_unisannio
Implementation of SZZ Algorithm.
This is a free open source implementation of the szz algorithm.
The algorithm works in two ways. In the first mode simply pass the local repository you want to analyze specifying the parameter "--repo-path". The analysis will be done using only the commit message contained in the commits. If you want to have a more precise information on bug inducing commits, you can specify the "-i" flag and pass the path to a local JSON file containing the data of the issues of the repository. For both of these you can specify the "-r" flag to obtain only the most recent bug inducing commit for each file, instead of all of them 

Specify the issue number pattern, used in the commit message relating to the bug fix commit, defined in the regular expression to retrieve the issue resolved by the commit bug fix in the file: 'regex_config.txt'
