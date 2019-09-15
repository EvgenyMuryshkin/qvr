using Drivers;
using FPGA;
using FPGA.Attributes;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace VRCamera
{
    [BoardConfig(Name = "Quokka")]
    public static class TestController
    {
        public static async Task Aggregator(
            // blinker
            FPGA.OutputSignal<bool> LED1,

            // IO banks for Quokka board, not needed for another boards
            FPGA.OutputSignal<bool> Bank1,
            FPGA.OutputSignal<bool> Bank2,
            FPGA.OutputSignal<bool> Bank5,

            // UART
            FPGA.InputSignal<bool> RXD,
            FPGA.OutputSignal<bool> TXD
            )
        {
            QuokkaBoard.OutputBank(Bank1);
            QuokkaBoard.InputBank(Bank2);
            QuokkaBoard.OutputBank(Bank5);
            IsAlive.Blink(LED1);

            bool internalTXD = true;
            FPGA.Config.Link(internalTXD, TXD);

            const int servosCount = 3;
            byte[] servosData = new byte[servosCount];

            Sequential servoHandler = () =>
            {
                uint instanceId = FPGA.Config.InstanceId();
                var servoOutputPin = new FPGA.OutputSignal<bool>();
                byte value = 0;
                bool servoOutput = false;
                byte requestValue = 0;

                FPGA.Config.Link(servoOutput, servoOutputPin);

                while (true)
                {
                    requestValue = servosData[instanceId];

                    if (requestValue != value)
                    {
                        if (requestValue < value)
                        {
                            value--;
                        }
                        else
                        {
                            value++;
                        }
                    }

                    MG996R.Write(value, out servoOutput);
                }
            };

            FPGA.Config.OnStartup(servoHandler, servosCount);

            Sequential readHandler = () =>
            {
                byte counter = 0;
                byte step = 5;
                while(true)
                {
                    while (counter < 180)
                    {
                        servosData[0] = counter;
                        servosData[1] = counter;
                        servosData[2] = counter;
                        counter += step;
                        FPGA.Runtime.Delay(TimeSpan.FromMilliseconds(100));
                    }

                    while (counter > 0)
                    {
                        servosData[0] = counter;
                        servosData[1] = counter;
                        servosData[2] = counter;
                        counter -= step;
                        FPGA.Runtime.Delay(TimeSpan.FromMilliseconds(100));
                    }
                }
            };

            FPGA.Config.OnStartup(readHandler);
        }
    }
}