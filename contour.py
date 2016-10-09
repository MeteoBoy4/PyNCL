#!/usr/bin/env python

import math

level = 300
pname = "div"
fmt	  = "ps"
lllat = -10.
lllon = 20.
urlat = 60.
urlon = 160.
input_directory = "/run/media/MeteoBoy4/Data/MData/ERA-Interim/2005/div/jan/upmonth/"
background_directory = "/run/media/MeteoBoy4/Data/MData/ERA-Interim/Surface_GeoP/"
input_file = "300hpa.nc"
variable_name = "d"
variable_standard_name = "Divergence"
Scale = True
scale = 1e5
power_scale = math.ceil(math.log(scale,10.))
FillOn = True
LinesOn = False
LabelsOn = False
Sym_color = False
Set_contour_levels= True
contour_levels = [8, -8, 1] # The maximum, minimum and spacing, respectively
Shorts	= True
levels_exist = False

topo_line = 2000.
zlllat = 20.
zlllon = 60.
zurlat = 45.
zurlon = 110.

if levels_exist:
	variable_slice_0 = 'variable(0, {lev}, {lllat:urlat}, {lllon:urlon})'
	variable_slice_n = 'variable(nmo, {lev}, {lllat:urlat}, {lllon:urlon})'
else:
	variable_slice_0 = 'variable(0, {lllat:urlat}, {lllon:urlon})'
	variable_slice_n = 'variable(nmo, {lllat:urlat}, {lllon:urlon})'


f = open('contour.ncl','w')

f.write("""load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"

begin
;------Define constants and parameters
""")

f.write("""
	lev     = {lev}
	pname   = "{pname}"+tostring(lev)
	fmt     = "{fmt}"

	lllat   = {lllat}
	lllon   = {lllon}
	urlat   = {urlat}
	urlon   = {urlon}

	zlllat   = {zlllat}
	zlllon   = {zlllon}
	zurlat   = {zurlat}
	zurlon   = {zurlon}
""".format(lev=level,pname=pname,fmt=fmt,lllat=lllat,lllon=lllon,urlat=urlat,urlon=urlon,
		zlllat=zlllat,zlllon=zlllon,zurlat=zurlat,zurlon=zurlon))

f.write("""
;------Read the data from ncfile and some other support data
	dirvar   = "{dirvar}"
	dirbac   = "{dirbac}"
	maskf=addfile("$NCARG_ROOT/lib/ncarg/data/cdf/landsea.nc","r")
	system("rm -f "+pname+"."+fmt)
	Vfile    = addfile(dirvar+"{inputf}","r")
	ofile = addfile(dirbac+"Surface_GeoP.nc","r")
""".format(dirvar=input_directory,dirbac=background_directory,inputf=input_file))

if Shorts:
	f.write('      	variable = short2flt(Vfile->{vari})'.format(vari=variable_name))
else:
	f.write('      	variable = Vfile->{vari}'.format(vari=variable_name))

if Scale:
	f.write("""
	variable = variable*{scale}""".format(scale=scale))

f.write("""
	time = Vfile->time
	printVarSummary(variable)
	z=short2flt(ofile->z(0,:,:))
	lsdata=maskf->LSMASK
	dims=dimsizes(variable)
	ntime=dims(0)
""")

f.write("""
;------Set for orography and masking the ocean
	z=z/9.80665
	lsm=landsea_mask(lsdata,z&latitude,z&longitude)
	z=mask(z,lsm.eq.0,False)
""")

f.write("""
;------Set up the map
	wks=gsn_open_wks(fmt,pname)

	cnres=True
	cnres@gsnDraw=False
	cnres@gsnFrame=False

	cnres@sfXCStartV=lllon
	cnres@sfXCEndV  =urlon
	cnres@sfYCStartV=lllat
	cnres@sfYCEndV  =urlat

	cnres@mpMinLonF=lllon
	cnres@mpMaxLonF=urlon
	cnres@mpMinLatF=lllat
	cnres@mpMaxLatF=urlat

	cnres@gsnMaximize=True
	cnres@gsnAddCyclic=False
	cnres@gsnPaperOrientation="portrait"

	cnres@cnFillOn={Fill}
	cnres@cnLinesOn={Lines}
	cnres@cnLineLabelsOn={Label}

	cnres@gsnLeftString=""
	cnres@gsnRightString=""
""".format(Fill=FillOn, Lines=LinesOn, Label=LabelsOn))

if Sym_color:
	f.write("""
	symMinMaxPlt({variable_slice},13,False,cnres)
""".format(variable_slice=variable_slice_0))
if Set_contour_levels:
	f.write("""
	cnres@cnLevelSelectionMode="ManualLevels"
	cnres@cnMaxLevelValF={max}
	cnres@cnMinLevelValF={min}
	cnres@cnLevelSpacingF={spacing}
""".format(max=contour_levels[0], min=contour_levels[1], spacing=contour_levels[2]))

f.write("""
	map=gsn_csm_contour_map(wks, {variable_slice}, cnres)
""".format(variable_slice=variable_slice_0))

f.write("""
	tpres=True
	tpres@gsnDraw=False
	tpres@gsnFrame=False
	tpres@gsnLeftString=""
	tpres@gsnRightString=""

	tpres@sfXCStartV=zlllon
	tpres@sfXCEndV=zurlon
	tpres@sfYCStartV=zlllat
	tpres@sfYCEndV=zurlat

	tpres@cnLineLabelsOn=False
	tpres@cnInfoLabelOn=False
	tpres@cnLevelSelectionMode="ExplicitLevels"
	tpres@cnLevels=(/{topo}/)
	tpres@cnLineThicknessF=3.0

	tpres@gsnMaximize=True
	tpres@gsnAddCyclic=False
	tpres@gsnPaperOrientation="portrait"

	tpres@tiMainFontHeightF=0.015
""".format(topo=topo_line))

if Scale:
    f.write("""
	tpres@tiMainString="{standard}"+tostring(lev)+" (10~S~-{power}~N~"+variable@units+")"+"     "+cd_string(time(0), \\
					"%H%MUTC %d%c %Y")
	""".format(standard=variable_standard_name, power=int(power_scale)))
else:
    f.write("""
	tpres@tiMainString="{standard}"+tostring(lev)+" ("+variable@units+")"+"     "+cd_string(time(0), \\
						"%H%MUTC %d%c %Y")
		""".format(standard=variable_standard_name))


f.write("""
	map2=gsn_csm_contour(wks,z({{zlllat:zurlat}},{{zlllon:zurlon}}),tpres)
	overlay(map,map2)
	draw(map)
	frame(wks)
""".format(topo=topo_line,standard=variable_standard_name))

if Scale:
	f.write("""
		nmos=ntime
		do nmo=1,nmos-1
			month=nmo+1
			tpres@tiMainString="{standard}"+tostring(lev)+" (10~S~-{power}~N~"+variable@units+")"+"     "+cd_string(time(nmo), \\
							"%H%MUTC %d%c %Y")
			tpres@tiMainFontHeightF=0.015
	""".format(standard=variable_standard_name, power=int(power_scale)))
else:
	f.write("""
		nmos=ntime
		do nmo=1,nmos-1
			month=nmo+1
			tpres@tiMainString="{standard}"+tostring(lev)+" ("+variable@units+")"+"     "+cd_string(time(nmo), \\
								"%H%MUTC %d%c %Y")
			tpres@tiMainFontHeightF=0.015
	""".format(standard=variable_standard_name))

if Sym_color:
	f.write("""
		symMinMaxPlt({variable_slice},13, False,cnres)
""".format(variable_slice=variable_slice_n))
if Set_contour_levels:
	f.write("""
		cnres@cnLevelSelectionMode="ManualLevels"
		cnres@cnMaxLevelValF={max}
		cnres@cnMinLevelValF={min}
		cnres@cnLevelSpacingF={spacing}
""".format(max=contour_levels[0], min=contour_levels[1], spacing=contour_levels[2]))


f.write("""
		map=gsn_csm_contour_map(wks, {variable_slice},cnres)
		map2=gsn_csm_contour(wks,z({{zlllat:zurlat}},{{zlllon:zurlon}}),tpres)
		overlay(map,map2)

		draw(map)
		frame(wks)
	end do
""".format(variable_slice=variable_slice_n))

f.write("""
	delete(variable)

end""")
