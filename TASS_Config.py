import m5
from m5.objects import *

import TASS_Implementation

system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Create heterogeneous CPU clusters
system.cluster0 = [ArmMinorCPU(cpu_id=i + 2) for i in range(2)]  # HP Cortex-A15 cores
system.cluster1 = [ArmO3CPU(cpu_id=i) for i in range(2)]  # LP Cortex-A7 cores

# Set up memory system
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]
system.membus = SystemXBar()

# Connect CPUs to memory bus
for cpu in system.cluster0 + system.cluster1:
    cpu.createInterruptController()
    cpu.connectAllPorts(system.membus)

system.thermal_model = ThermalModel()
system.power_model = PowerModel()

# Create workload
process = Process()
process.cmd = ['path/to/benchmark']
for cpu in system.cluster0 + system.cluster1:
    cpu.workload = process

system.tass_scheduler = TASS_Implementation.TaskScheduler(system)

root = Root(full_system=False, system=system)
m5.instantiate()

print("Simulation starts")
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))
