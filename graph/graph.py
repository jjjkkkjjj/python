import matplotlib.pyplot as plt
import numpy as np

x = [100, 250, 500, 750, 1000, 5000]
y = [61, 63, 75, 75, 69, 65]

plt.figure(figsize=(2,1))
plt.rcParams['font.size'] = 24
plt.plot(x, y, '-o')
#plt.title('LOPO result')
plt.xlabel('C')
plt.xlim([80,10000])
plt.ylim([60,77])
plt.ylabel('accuracy')
plt.xscale('log')
plt.grid(which='both')
plt.show()
