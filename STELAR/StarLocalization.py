import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import numpy as np
import os
from ttkbootstrap.toast import ToastNotification
matplotlib.use('Agg')

path = '/home/gomes/MEGA/Workspaces/STELAR_project/STELAR/'
output = '/home/gomes/MEGA/Workspaces/STELAR_project/outputs/'
isocfit_outputs = output + 'isocrone_fit/'
isocs = path + 'isochrone_models/'
os.chdir(path)


def readiso(model):
    global Ntabage, Nlinesa, Ncoluma, ageiso, tablenames, sptype, it, il, ia, im, at, al, am, evoltracks, isoctables

    if model == "Siess 2000":
        evoltracks = isocs + 'SIESS/Grid/OV02/'
        isoctables = isocs + 'SIESS/Isoc/'
        Ntabage = 9
        Nlinesa = 12
        Ncoluma = 21
        ageiso = np.array([1.e4, 5.e4, 2.e5, 5.e5, 2.e6, 5.e6, 1.e7, 6e7, 1e8])

        tablenames = ['zamsZ002oiso1e4.dat', 'zamsZ002oiso5e4.dat', 'zamsZ002oiso2e5.dat',
                      'zamsZ002oiso5e5.dat', 'zamsZ002oiso2e6.dat', 'zamsZ002oiso5e6.dat',
                      'zamsZ002oiso1e7.dat', 'zamsZ002oiso6e7.dat', 'zamsZ002oiso1e8.dat']
        # evolutionary tracks table index for temperature, luminosity, age and mass
        it = 6
        il = 2
        ia = 10
        im = 9
        #  Isochrones table index for luminosity, temperature and mass
        al = 1
        at = 3
        am = 4
    elif model == "BHAC15":
        evoltracks = isocs + 'BAHC15/Grid/BWeLM/'
        isoctables = isocs + 'BAHC15/Isoc/'
        Ntabage = 10
        Nlinesa = 30
        Ncoluma = 9

        ageiso = [5.e5, 1.e6, 5.e6, 1.e7, 2e6, 2.e7, 8.e7, 1.e8, 1.2e8, 2e8]

        tablenames = ['bahc15iso5e5.dat', 'bahc15iso1e6.dat', 'bahc15iso5e6.dat',
                      'bahc15iso1e7.dat', 'bahc15iso2e6.dat', 'bahc15iso2e7.dat', 'bahc15iso8e7.dat',
                      'bahc15iso1e8.dat', 'bahc15iso1.2e8.dat', 'bahc15iso2e8.dat']
        # isocrhones table index for temperature, luminosity, age and mass
        it = 2
        il = 3
        ia = 1
        im = 0
        # evolutionary tracks index for luminosity, temperature and mass
        al = 2
        at = 1
        am = 0

    sptype = ['M', 'K', 'G', 'F', 'A', 'B', 'O']

    alldataiso = np.zeros((Ntabage, Ncoluma, Nlinesa))
    dataiso = np.zeros((Ncoluma, Nlinesa))

    for i in range(Ntabage):
        file = isoctables + tablenames[i].strip()
        with open(file, 'r') as f:
            for j in range(Nlinesa):
                line = f.readline().split()
                for k in range(Ncoluma):
                    dataiso[k, j] = float(line[k])
        alldataiso[i, :, :] = dataiso[:, :]

    return alldataiso


def tablestr(Ntables):
    mass = [(x+1) / 10 for x in range(Ntables)]
    imass = []

    for i in range(Ntables):
        if i <= 8:
            imass.append('m0.' + str(i + 1) + 'z02d02.hrd')

        else:
            imass.append('m' + str((i + 1) / 10) + 'z02d02.hrd')
    return mass, imass


def interp(t1, l1, var, Nlines, alldataiso):
    """
    This code is a Python function called interp that performs interpolation
    and plotting tasks to find the nearest evolutionary track and isochrone
    for a star based on its temperature (t1) and luminosity (l1). It also plots
    the results and saves the information into a file.
    """
    global nearage, nearmasst, nAge, nMass, y
    # Parameters
    tmax = 1.e14
    tol = 1.e-2
    if il == 3:
        l1 = 10. ** l1

    # Data arrays
    x = np.arange(len(var[0]))
    dl = np.zeros(len(x))
    dt = t1 - var[it]
    dl[:] = l1 - var[il]
    y = np.sqrt(dl ** 2 + dt ** 2)
    z = np.gradient(y, x)

    # Finding nearest pair
    tmax_index = np.argmin(y)
    nearmasst = var[im][tmax_index]
    nearage = var[ia][tmax_index]
    if ia == 1:
        nearage = 10 ** nearage

    nfac = int((10 * nearmasst))

    ic = Nlines[nfac - 1]

    if 2 <= nfac <= 11:
        i1 = int(np.sum(Nlines[:nfac - 1]))
        i2 = int(np.sum(Nlines[:nfac])) - 1

        ic2 = Nlines[nfac - 2]

        i3 = 0 if nfac == 2 else int(np.sum(Nlines[:nfac - 2]))
        i4 = Nlines[0] - 1 if nfac == 2 else int(np.sum(Nlines[:nfac - 1])) - 1

        x2 = var[it][i3:i4]
        y2 = var[il][i3:i4]

        ic3 = Nlines[nfac]

        i5 = int(np.sum(Nlines[:nfac]))
        i6 = int(np.sum(Nlines[:nfac + 1])) - 1

        x3 = var[it][i5:i6]
        y3 = var[il][i5:i6]

    if nfac == 1:
        i1 = 0
        i2 = Nlines[0] - 1

        ic3 = Nlines[nfac]

        i5 = int(np.sum(Nlines[:nfac]))
        i6 = int(np.sum(Nlines[:nfac + 1]) - 1)

        x3 = var[it][i5:i6]
        y3 = var[il][i5:i6]

    if nfac == 12:
        i1 = int(np.sum(Nlines[:nfac - 1]))
        i2 = int(np.sum(Nlines[:nfac]) - 1)

        ic2 = Nlines[nfac - 2]

        i3 = int(np.sum(Nlines[:nfac - 2]))
        i4 = int(np.sum(Nlines[:nfac - 1]) - 1)

        x2 = var[it][i3:i4]
        y2 = var[il][i3:i4]

    x1 = var[it][i1:i2]
    y1 = var[il][i1:i2]

    maxT = 1.e14
    indmass = 0
    itab = None
    for i in range(Ntabage):
        for k in range(Nlinesa):
            aux1 = np.sqrt((alldataiso[i][al][k] - l1) ** 2)
            aux2 = alldataiso[i][am][k]
            if aux2 == nearmasst and aux1 < maxT:
                maxT = aux1
                itab = i
                indmass = k

    if itab is not None:

        orderedage = np.sort(ageiso)

        # Plotting
        fig = plt.figure(figsize=(10, 12), tight_layout=True)
        gs = gridspec.GridSpec(3, 2)
        axs = fig.add_subplot(gs[2, 0])
        axs.plot(x, y, label='$\delta$', marker='o', color='#3F8D4F', mfc='w')
        axs.set_title('$\delta = \sqrt{[(T_{\mathrm{eff}} - T_i)^2 - (L - L_i)^2]}$')
        axs.set_xlabel('$x_i$')
        axs.set_ylabel('$\delta$')
        axs.grid()

        axs = fig.add_subplot(gs[2, 1])
        axs.plot(x, z, label='Derivative z = d$\delta$/dx', color='#7A306C', mfc='w')
        axs.set_title('Derivative z = d$\delta$/dx')
        axs.set_xlabel('i')
        axs.set_ylabel('z')
        axs.set_ylim(-10, 10)
        axs.grid()

        ii = None
        for i in range(Ntabage):
            iaux = orderedage[i]
            if iaux == ageiso[itab]:
                ii = i

        if ii is not None and 1 <= ii < 8:
            inew = ii
            inew1 = ii - 1
            inew2 = ii + 1

            axs = fig.add_subplot(gs[:2, :])
            axs.plot(alldataiso[inew1, at, :], (alldataiso[inew1, al, :]), label=f'{orderedage[inew1] / 1e6} Myr',
                     color='#3F8D4F')
            axs.plot(alldataiso[inew, at, :], (alldataiso[inew, al, :]), label=f'{orderedage[inew] / 1e6} Myr',
                     color='black')
            axs.plot(alldataiso[inew2, at, :], (alldataiso[inew2, al, :]), label=f'{orderedage[inew2] / 1e6} Myr',
                     color='#7A306C')

        if ii == 0:
            inew = ii
            inew1 = ii + 1

            axs.plot(alldataiso[inew, at, :], (alldataiso[inew, al, :]), label=f'{orderedage[inew] / 1e6} Myr',
                     color='black')
            axs.plot(alldataiso[inew1, at, :], (alldataiso[inew1, al, :]), label=f'{orderedage[inew1] / 1e6} Myr',
                     color='#7A306C')

        if ii == 9:
            inew = ii
            inew1 = ii - 1

            axs.plot(alldataiso[inew, at, :], (alldataiso[inew, al, :]), label=f'{orderedage[inew] / 1e6} Myr',
                     color='black')
            axs.plot(alldataiso[inew1, at, :], (alldataiso[inew1, al, :]), label=f'{orderedage[inew1] / 1e6} Myr',
                     color='#3F8D4F')

        if 2 <= nfac <= 10:
            axs.plot(x2, y2, '--', label=f'M = 0.{nfac - 1} M$_\odot$', color='#3F8D4F')
            axs.plot(x1, y1, '--', label=f'M = 0.{nfac} M$_\odot$', color='black')
            axs.plot(x3, y3, '--', label=f'M = 0.{nfac + 1} M$_\odot$', color='#7A306C')
        if nfac == 1:
            axs.plot(x1, y1, '--', label=f'M = 0.{nfac} M$_\odot$', color='black')
            axs.plot(x3, y3, '--', label=f'M = 0.{nfac + 1} M$_\odot$', color='#7A306C')
        if nfac == 12:
            axs.plot(x2, y2, '--', label=f'M = 0.{nfac - 1} M$_\odot$', color='#3F8D4F')
            axs.plot(x1, y1, '--', label=f'M = 1.2 M$_\odot$', color='black')

        axs.scatter(t1, l1, color='red', marker='*', label='Star', edgecolors='white', s=300)

        axs.set_title('HR Diagram')
        axs.set_xlabel('T$_{\mathrm{eff}}$ (K)')
        axs.set_ylabel('L/L$_\odot$')
        axs.grid()
        axs.set_yscale('log')
        axs.legend()
        plt.gca().invert_xaxis()
        plt.savefig(f"{output}isocfit_outputs/hrd_star_{l1}_{t1}_{nearage / 1e6}_{nearmasst}.pdf", dpi=300)
        plt.close(fig)
        plt.close()

        nearage = ageiso[itab]
        nearage = float(nearage) / 1e6
        if il == 3:
            return nearage, nearmasst, t1, np.log10(l1)
        else:
            return nearage, nearmasst, t1, l1
    else:
        if il == 3:
            return None, None, t1, np.log10(l1)
        else:
            return None, None, t1, l1


def readtables(Ntables, imass, model):
    global colunas, Ncolumn, itot
    Nlines = 0
    if model == "Siess 2000":
        Ncolumn = 11  # Number of columns of each table
        Nlines = [228, 240, 228, 240, 264, 264, 312, 348, 372, 396, 384, 384]  # Number of lines of each table

    elif model == "BHAC15":
        Ncolumn = 13
        Nlines = [432, 432, 432, 432, 432, 432, 432, 432, 432, 424, 411, 397]
    itot = sum(Nlines)  # Total number of lines (all tables)
    var = np.zeros((Ncolumn, itot))  # A huge table with all data
    filedata = []
    for ind in imass:
        filedata.append(evoltracks + ind)

    initialine = np.zeros(Ntables, dtype=int)  # Limits of each table (inside the whole all-data table)
    finaline = np.zeros(Ntables, dtype=int)

    icount = -1

    for j in range(Ntables):
        aux = np.zeros((Ncolumn, Nlines[j]))
        with open(filedata[j], 'r') as f:
            for k in range(Nlines[j]):
                line = f.readline().split()
                for m in range(Ncolumn):
                    aux[m, k] = float(line[m])

                icount += 1
                var[:, icount] = aux[:, k]

        # Update initial and final lines for the current table
        if j == 0:
            initialine[j] = 0
            finaline[j] = Nlines[j] - 1
        else:
            initialine[j] = finaline[j - 1] + 1
            finaline[j] = finaline[j - 1] + Nlines[j]

    return var, Nlines, initialine, finaline


def intpol(model):
    global nearage, nearmasst, nAge, nMass, y, mass, imass

    Ntables = 12

    mass, imass = tablestr(Ntables)

    # Read isochrones data
    alldataiso = readiso(model)

    # Read tables
    var, Nlines, initialine, finaline = readtables(Ntables, imass, model)

    return var, Nlines, alldataiso


def plot_HRD(result, model):
    var, Nlines, alldataiso = intpol(model)

    colors = [cm.Purples(i) for i in np.linspace(0.5, 1, len(imass))]
    colors_ = [cm.Greens(i) for i in np.linspace(0.5, 1, len(imass))]
    fig = plt.figure(figsize=(10, 8), tight_layout=True)
    for j in range(len(var[:, im, 0])):
        plt.plot(var[it, :], np.log10(var[il, :]), label=f'Mass: {mass[j]}',
                 color=colors[j])

    orderedage = np.sort(ageiso)

    for i in range(len(alldataiso[:, am, 0])):
        plt.plot(alldataiso[i, at, :], np.log10(alldataiso[i, al, :]), label=f'{orderedage[i] / 1e6} Myr',
                 color=colors_[i], linestyle='dashed')
    plt. scatter(result['Teff'], result['logL'], marker='^', color='brown')
    plt.xlabel('T$_{eff}$ (K)')
    plt.ylabel('log L/L$_\odot$')
    plt.xlim(6000, 2500)
    plt.title('HR Diagram')
    plt.grid(True)
    plt.legend(loc='best', fontsize='small', frameon=True, borderpad=1, borderaxespad=1, ncol=2)
    plt.savefig(isocfit_outputs + 'hrd_complete.pdf', dpi=300)

