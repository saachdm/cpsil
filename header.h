#ifndef HEADER
#define HEADER

// "Outgoing" --> To python
// "Incoming" --> From python
typedef struct data_outgoing{
    float prop_input;
    float brake_input;
    int gear_input;
} data_outgoing_type;

typedef struct data_incoming{
    float Vx;
    float Vx_ref;
} data_incoming_type;

// typedef struct data_incoming_mode{
//     float yyyy;
//     float zzzz;
// } data_incoming_mode_type;

#endif