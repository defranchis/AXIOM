void sort(){

	// open data
	ifstream fin("channels128_map_from_schematics.txt");

	double channel[144];
	double channelName[144];
	int index[144];

	Int_t i =0 ;
  	while (fin.good()) {
    	fin >> channel[i]>> channelName[i];
    	//cout << channel[i] << endl;
       	i++;
	}


	TMath::Sort(144,channelName, index, false);
	//cout << channel[index[0]] << " " << channelName[index[0]] << endl;
	

	for(int j=0;j<144;j++){
		cout << channel[index[j]] << " " << channelName[index[j]] << endl;
		//cout << channel[index[j]] << endl;
	}
}