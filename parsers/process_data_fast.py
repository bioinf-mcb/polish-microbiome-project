import glob
from process_data import process
import tqdm

if __name__=="__main__":
    import threading
    THREADS = 4

    queue = []
    for fname in tqdm.tqdm(glob.glob("/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload/pacjenci 201-250/*/*.xls")):
        queue.append(threading.Thread(target=process, args=(fname,)))
        queue[-1].start()
        if len(queue)>=THREADS:
            for i in queue:
                i.join()
            queue = []


            