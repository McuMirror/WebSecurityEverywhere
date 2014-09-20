/*
  Name:     upis.c
  Author:   Graham Single
  Revision: 1.00
  Date:     20-Apr-14
  Purpose:  Reports UPiS PICo interface values in Raspberry Pi command line
*/

/*
Adapted by Arcadia Labs / Stephane Guerreau
Revision : 1.0
Date : 19-Sept-14
Modifications :
	- removed line breaks and units for proper use in python script
*/

#include <linux/i2c-dev.h>
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>

/* minimum required number of parameters */
#define MIN_REQUIRED 2
#define MAX_REQUIRED 2

/* display usage */
int help() {
   printf("Usage: upis [OPTION]\n");
   printf("Return information from the Raspberry Pi UPiS Power Supply\n\n");
   printf("  -p\tReturn an integer representing the current UPiS power source\n");
   printf("  -P\tReturn a string with a description of the current UPiS power source\n");
   printf("  -c\tReturn the UPiS temperature in centigrade\n");
   printf("  -f\tReturn the UPiS temperature in fahrenheit\n");
   printf("  -a\tReturn the UPiS+RPi current consumption in mA\n");
   printf("  -b\tReturn the UPiS battery voltage in V\n");
   printf("  -r\tReturn the RPi input voltage in V\n");
   printf("  -u\tReturn the UPiS USB power input voltage in V\n");
   printf("  -e\tReturn the UPiS external power input voltage in V\n");
   return 1;
}

/* main */
int main(int argc, char *argv[]) {
  if (argc < MIN_REQUIRED || argc > MAX_REQUIRED ) {
     return help();
  }

  int i2cfile;
  int i2cbus = 1; /* 0 for 256MB Model A, 1 for 512MB Model B */
  char i2cdev[20];

  snprintf(i2cdev, 19, "/dev/i2c-%d", i2cbus);
  i2cfile = open(i2cdev, O_RDWR);
  if (i2cfile < 0) {
    /* Unable to open I2C device */
    printf("Error: Unable to open i2c bus %u\n",i2cbus);
    exit(1);
  }

  int i2caddr = 0x6A; /* The i2c address for the UPiS PiCO interface*/
  if (ioctl(i2cfile, I2C_SLAVE, i2caddr) < 0) {
    /* Unable to read the PiCO interface */
    printf("Error: Unable to access the PiCO interface at address 0x%02x\n",i2cbus);
    exit(2);
  }

  int argctr;

  /* iterate over all arguments */
  for (argctr = 1; argctr < argc; argctr++) {
    if (strcmp("-p", argv[argctr]) == 0) {
      /* Integer represenation of power source */

      __u8 i2c_register = 0x00; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_byte_data(i2cfile, i2c_register);
      if (i2cresult < 1 || i2cresult > 5 ) {
        printf("Error: Unexpected result for power mode: u\n",i2cresult);
      } else {
        printf("%u",i2cresult);
      }
      continue;
    }
    if (strcmp("-P", argv[argctr]) == 0)
    {
      /* String represenation of power source */

      __u8 i2c_register = 0x00; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_byte_data(i2cfile, i2c_register);
      if (i2cresult < 1 || i2cresult > 5 )
      {
        printf("Error: Unexpected result for power mode: u\n",i2cresult);
      } else {
        switch (i2cresult)
        {
          case 1:
            printf("External Power [EPR]\n");
            break;
          case 2:
            printf("UPiS USB Power [USB]\n");
            break;
          case 3:
            printf("Raspberry Pi USB Power [RPI]\n");
            break;
          case 4:
            printf("Battery Power [BAT]\n");
            break;
          case 5:
            printf("Low Power [LPR]\n");
            break;
        }
      }
      continue;
    }
    if (strcmp("-b", argv[argctr]) == 0)
    {
      /* Battery voltage */

      __u8 i2c_register = 0x01; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_word_data(i2cfile, i2c_register);
      if (i2cresult < 0 )
      {
        printf("Error: Unexpected result for battery voltage: u\n",i2cresult);
      } else {
        printf("%g",(float)bcdword2dec(i2cresult)/(float)100);
      }
      continue;
    }
    if (strcmp("-r", argv[argctr]) == 0)
    {
      /* RPi input voltage */

      __u8 i2c_register = 0x03; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_word_data(i2cfile, i2c_register);
      if (i2cresult < 0 )
      {
        printf("Error: Unexpected result for RPi voltage: u\n",i2cresult);
      } else {
        printf("%g",(float)bcdword2dec(i2cresult)/(float)100);
      }
      continue;
    }
    if (strcmp("-u", argv[argctr]) == 0)
    {
      /* UPiS USB input voltage */

      __u8 i2c_register = 0x05; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_word_data(i2cfile, i2c_register);
      if (i2cresult < 0 )
      {
        printf("Error: Unexpected result for UPiS USB input voltage: u\n",i2cresult);
      } else {
        printf("%g",(float)bcdword2dec(i2cresult)/(float)100);
      }
      continue;
    }
    if (strcmp("-e", argv[argctr]) == 0)
    {
      /* External power voltage */

      __u8 i2c_register = 0x07; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_word_data(i2cfile, i2c_register);
      if (i2cresult < 0 )
      {
        printf("Error: Unexpected result for external power voltage: u\n",i2cresult);
      } else {
        printf("%g",(float)bcdword2dec(i2cresult)/(float)100);
      }
      continue;
    }
    if (strcmp("-a", argv[argctr]) == 0)
    {
      /* Current draw */

      __u8 i2c_register = 0x09; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_word_data(i2cfile, i2c_register);
      if (i2cresult < 0 )
      {
        printf("Error: Unexpected result for current consumption: u\n",i2cresult);
      } else {
        printf("%i",bcdword2dec(i2cresult));
      }
      continue;
    }
    if (strcmp("-c", argv[argctr]) == 0) {
      /* Temperature in C */

      __u8 i2c_register = 0x0B; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_byte_data(i2cfile, i2c_register);
      if (i2cresult < 0 ) {
        printf("Error: Unexpected result for temperature in C: %u\n",i2cresult);
      } else {
        printf("%u",bcdbyte2dec(i2cresult));
      }
      continue;
    }
    if (strcmp("-f", argv[argctr]) == 0) {
      /* Temperature in F */

      __u8 i2c_register = 0x0C; /* Device register to access */
      __s32 i2cresult;
      char buf[10];

      i2cresult = i2c_smbus_read_word_data(i2cfile, i2c_register);
      if (i2cresult < 0 ) {
        printf("Error: Unexpected result for temperature in F: %u\n",i2cresult);
      } else {
        printf("%u",bcdword2dec(i2cresult));
      }
      continue;
    }
    return help();
  }
  return 0;
}

int bcdword2dec(unsigned int bcd)
{
  int a;
  int b;
  int c;
  int d;
  a = (bcd >> 12)&0x000F;
  b = (bcd >> 8)&0x000F;
  c = (bcd >> 4)&0x000F;
  d = bcd&0x000F;
  return((a*1000)+(b*100)+(c*10)+d);
}

int bcdbyte2dec(unsigned int bcd)
{
  int a;
  int b;
  a = (bcd >> 4)&0x000F;
  b = bcd&0x000F;
  return((a*10)+b);
}
