#ifndef _SYNAPSE_CPP
#define _SYNAPSE_CPP

#include "iostream"
#include "cmath"
#include "synapse.h"

SYNAPSE::SYNAPSE(void) {

        std::cin >> sourceNeuronIndex;

        std::cin >> targetNeuronIndex;

	    std::cin >> start_weight;

	    std::cin >> end_weight;

	    std::cin >> start_time;

	    std::cin >> end_time;

}

SYNAPSE::~SYNAPSE(void) {

}

int SYNAPSE::Get_Source_Neuron_Index(void) {

	return sourceNeuronIndex;
}

int SYNAPSE::Get_Target_Neuron_Index(void) {

        return targetNeuronIndex;
}

double SYNAPSE::Get_Weight(void) {

        return weight;
}

void SYNAPSE::Update_Weight(int t){

    if (t < start_time){
        weight = start_weight;
    }

	if ( (t >= start_time) and (t < end_time) and (end_time > start_time) ) {
        weight = weight + (end_weight - start_weight) / double(end_time - start_time);
	}

	if ( t > end_time ) {
        weight = end_weight;
	}

	if ( isnan(weight) ){
			std::cerr << " weight is nan ";
		}
}

void SYNAPSE::Print(void) {

	    std::cerr << sourceNeuronIndex << " ";

        std::cerr << targetNeuronIndex << " ";

        std::cerr << start_weight << " ";

        std::cerr << end_weight << " ";

        std::cerr << start_time << " ";

        std::cerr << end_time << " ";

}

#endif