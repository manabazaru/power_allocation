fig3 = plt.figure()
plt.scatter(haps_xy_arr[:,0], haps_xy_arr[:,1], s=10, c=haps_sinr_db_arr, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.clim(0, 40)
plt.colorbar()
plt.show()

fig3 = plt.figure()
plt.scatter(haps_xy_arr[:,0], haps_xy_arr[:,1], s=10, c=haps_sinr_db_arr2, cmap='jet')
plt.xlim(-haps_com_r, haps_com_r)
plt.ylim(-haps_com_r, haps_com_r)
plt.clim(0,40)
plt.colorbar()
plt.show()
