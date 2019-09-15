using Quokka.Core.Bootstrap;
using System;
using System.IO;
using System.Linq;

namespace cli
{
    class Program
    {
        static string SolutionDir(string path = null)
        {
            path = path ?? Directory.GetCurrentDirectory();

            if (Directory.EnumerateFiles(path, "*.sln").Any())
                return path;

            return SolutionDir(Path.GetDirectoryName(path));
        }

        static void Main(string[] args)
        {
            //var hdl = "vhdl";
            var hdl = "verilog";

            var qargs = new string[]
            {
                "-s",
                Path.Combine(SolutionDir(), "qvr"),
                // "-w", // watch for changes
                "-c",
                $"{hdl}.json"
            };

            QuokkaRunner.Default(qargs);
        }
    }
}
