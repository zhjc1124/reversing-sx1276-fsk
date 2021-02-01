#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdint.h>

uint8_t preamble[] = {0xaa, 0xaa, 0xaa, 0xaa, 0xaa};
uint8_t sync_word[] = {0xc1, 0x94, 0xc1};
uint8_t whitening_seq[] = {0xff, 0x87, 0xb8, 0x59, 0xb7, 0xa1, 0xcc, 0x24, 0x57, 0x5e, 0x4b, 0x9c, 0xe, 0xe9, 0xea, 0x50, 0x2a, 0xbe, 0xb4, 0x1b, 0xb6, 0xb0, 0x5d, 0xf1, 0xe6, 0x9a, 0xe3, 0x45, 0xfd, 0x2c, 0x53, 0x18, 0xc, 0xca, 0xc9, 0xfb, 0x49, 0x37, 0xe5, 0xa8, 0x51, 0x3b, 0x2f, 0x61, 0xaa, 0x72, 0x18, 0x84, 0x2, 0x23};
uint16_t CRC_calc(uint8_t *buffer, uint8_t bufferLength)
{
    uint16_t crc = 0x1D0F;
    uint16_t poly = 0x1021;

    uint8_t i;
    for(i = 0; i < bufferLength; i++)
    {
        uint8_t data = buffer[i];
        uint8_t j;
        for(j = 0; j < 8; j++)
        {
            if( (( (crc & 0x8000) >> 8 ) ^ (data & 0x80)) != 0 )
            {
                crc <<= 1;
                crc ^= poly;
            }
            else
            {
                crc <<= 1;
            }
            data <<= 1;
        }
    }
    return (uint16_t)(~crc);
}

uint8_t * make_packet(uint8_t* message, uint8_t length)
{
    uint8_t i;

    uint8_t payload[length+1];
    payload[0] = length;
    for(i = 0; i < length; i++)
    {   
        payload[i+1] = message[i];
    }
    uint16_t crc;
    crc = CRC_calc(payload, 3);

    uint8_t *packet;
    for(i = 0; i < 5; i++)
    {
        packet[i] = preamble[i];
    }
    for(i = 0; i < 3; i++)
    {
        packet[5+i] = sync_word[i];
    }
    for(i = 0; i < length+1; i++)
    {   
        
        packet[5+3+i] = payload[i] ^ whitening_seq[i];
    }
    
    packet[5+3+length+1] = (uint8_t)((crc & 0xff00) >> 8) ^ whitening_seq[length+1];
    packet[5+3+length+2] = (uint8_t)(crc & 0x00ff) ^ whitening_seq[length+2];
    return packet;
}

int main()
{
    uint8_t i;

    uint8_t message[] = {1, 2};
    uint8_t length = 2;

    uint8_t *packet = make_packet(message, length);
    uint8_t packet_len = 5+3+1+length+2;
     
    for(i = 0; i < packet_len; i++)
    {
        printf("0x%02x ", packet[i]);
    }
    printf("\n");
    return 0;
}



