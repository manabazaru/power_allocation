import path
import simulation as sim

def main():
    path.set_cur_dir()
    #sim.save_AUS_flops(3, [3600], [int(i) for i in range(1, 11)], 20)
    sim.save_MRUS_flops(3, [1800, 3600], [int(i) for i in range(1, 11)], 20, [3])

if __name__=='__main__':
    main()