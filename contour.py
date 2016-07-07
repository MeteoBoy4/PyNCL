#!/usr/bin/env python

import math

level = 500
pname = "pv"
fmt	  = "ps"
lllat = -10.
lllon = 20.
urlat = 60.
urlon = 160.
topo_line = 1500.
input_directory = "/run/media/MeteoBoy4/Data/MData/ERA-Interim/2013/PV/"
background_directory = "/run/media/MeteoBoy4/Data/MData/ERA-Interim/Surface_GeoP/"
input_file = "PV500.nc"
variable_name = "pv"
variable_standard_name = "Potential Vorticity"
scale = 1e6
power_scale = math.ceil(math.log(scale,10.))
FillOn = True
LinesOn = False
LabelsOn = False
Sym_color = False
Shorts	= True


f = open('contour.ncl','w')

f.write("""load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"

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
""".format(lev=level,pname=pname,fmt=fmt,lllat=lllat,lllon=lllon,urlat=urlat,urlon=urlon))

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

if scale:
	f.write("""
	variable = variable*{scale}""".format(scale=scale))

f.write("""
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
""".format(Fill=FillOn,Lines=LinesOn,Label=LabelsOn))

if scale:
	f.write("""
	cnres@gsnRightString="10~S~-{power}~N~"+variable@units
""".format(power=int(power_scale)))
else:
	f.write("""
	cnres@gsnRightString=variable@units
""")

if Sym_color:
	f.write("""
	symMinMaxPlt(variable(0,{lev},{lllat:urlat},{lllon:urlon}),12,False,cnres)
""")

f.write("""
	map=gsn_csm_contour_map(wks,variable(0,{lev},{lllat:urlat},{lllon:urlon}),cnres)
""")

f.write("""
	tpres=True
	tpres@gsnDraw=False
	tpres@gsnFrame=False
	tpres@gsnLeftString=""
	tpres@gsnRightString=""

	tpres@sfXCStartV=lllon
	tpres@sfXCEndV=urlon
	tpres@sfYCStartV=lllat
	tpres@sfYCEndV=urlat

	tpres@cnLineLabelsOn=False
	tpres@cnInfoLabelOn=False
	tpres@cnLevelSelectionMode="ExplicitLevels"
	tpres@cnLevels=(/{topo}/)
	tpres@cnLineThicknessF=3.0

	tpres@gsnMaximize=True
	tpres@gsnAddCyclic=False
	tpres@gsnPaperOrientation="portrait"

	tpres@tiMainFontHeightF=0.015
	tpres@tiMainString="{standard} on "+tostring(lev)+" hPa in 1th month (climatology)"

	map2=gsn_csm_contour(wks,z({{lllat:urlat}},{{lllon:urlon}}),tpres)
	overlay(map,map2)
	draw(map)
	frame(wks)
""".format(topo=topo_line,standard=variable_standard_name))

f.write("""
	nmos=ntime
	do nmo=1,nmos-1
		month=nmo+1
		tpres@tiMainString="{standard} on "+tostring(lev)+" hPa in "+month+"th month (climatology)"
		tpres@tiMainFontHeightF=0.015
""".format(standard=variable_standard_name))

if Sym_color:
	f.write("""
		symMinMaxPlt(variable(nmo,{lev},{lllat:urlat},{lllon:urlon}),12,False,cnres)
""")

f.write("""
		map=gsn_csm_contour_map(wks,variable(nmo,{lev},{lllat:urlat},{lllon:urlon}),cnres)
		map2=gsn_csm_contour(wks,z({lllat:urlat},{lllon:urlon}),tpres)
		overlay(map,map2)

		draw(map)
		frame(wks)
	end do
""")

f.write("""
	delete(variable)

end""")
