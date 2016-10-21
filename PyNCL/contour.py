#!/home/meteoboy4/anaconda/bin/python

import math


class Contour(object):
    def __init__(self, **kwargs):
        prop_defaults = {
            "levels_exist": False,
            "level": 300,
            "pname": "div",
            "fmt": "ps",
            "lllat": -10.,
            "lllon": 20.,
            "urlat": 60.,
            "urlon": 160.,
            "input_directory": None,
            "background_directory": "/run/media/MeteoBoy4/Data/MData/ERA-Interim/Surface_GeoP/",
            "input_file": None,
            "variable_name": "d",
            "variable_standard_name": "Divergence",
            "Scale": True,
            "scale": 1e5,
            "FillOn": True,
            "LinesOn": False,
            "LabelsOn": False,
            "Sym_color": False,
            "Set_contour_levels": True,
            "contour_levels": [8, -8, 1],  # The maximum, minimum and spacing, respectively
            "Shorts": True,
            "topo_line": 2000.,
            "zlllat": 20.,
            "zlllon": 60.,
            "zurlat": 45.,
            "zurlon": 110.
        }

        for (prop, default) in prop_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))

        self.power_scale = math.ceil(math.log(self.scale, 10.))

        if self.levels_exist:
            self.variable_slice_0 = 'variable(0, {lev}, {lllat:urlat}, {lllon:urlon})'
            self.variable_slice_n = 'variable(nmo, {lev}, {lllat:urlat}, {lllon:urlon})'
        else:
            self.variable_slice_0 = 'variable(0, {lllat:urlat}, {lllon:urlon})'
            self.variable_slice_n = 'variable(nmo, {lllat:urlat}, {lllon:urlon})'

    def script_creator(self):
        self.script = open('contour.ncl', 'w')

    def header(self):
        self.script.write("""load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
        load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
        load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
        load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
        load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"

        begin
        ;------Define constants and parameters
        """)

    def parameter_define(self):
        self.script.write("""
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
""".format(lev=self.level, pname=self.pname, fmt=self.fmt, lllat=self.lllat, lllon=self.lllon, urlat=self.urlat,
       urlon=self.urlon, zlllat=self.zlllat, zlllon=self.zlllon, zurlat=self.zurlat, zurlon=self.zurlon))

    def variable_reader(self):
        self.script.write("""
;------Read the data from ncfile and some other support data
dirvar   = "{dirvar}"
dirbac   = "{dirbac}"
maskf=addfile("$NCARG_ROOT/lib/ncarg/data/cdf/landsea.nc","r")
system("rm -f "+pname+"."+fmt)
Vfile    = addfile(dirvar+"{inputf}","r")
ofile = addfile(dirbac+"Surface_GeoP.nc","r")
""".format(dirvar=self.input_directory, dirbac=self.background_directory, inputf=self.input_file))

        if self.Shorts:
            self.script.write('      	variable = short2flt(Vfile->{vari})'.format(vari=self.variable_name))
        else:
            self.script.write('      	variable = Vfile->{vari}'.format(vari=self.variable_name))

        if self.Scale:
            self.script.write("""
            variable = variable*{scale}""".format(scale=self.scale))

        self.script.write("""
            time = Vfile->time
            printVarSummary(variable)
            z=short2flt(ofile->z(0,:,:))
            lsdata=maskf->LSMASK
            dims=dimsizes(variable)
            ntime=dims(0)
        """)

    def orography_setter(self):
        self.script.write("""
        ;------Set for orography and masking the ocean
            z=z/9.80665
            lsm=landsea_mask(lsdata,z&latitude,z&longitude)
            z=mask(z,lsm.eq.0,False)
        """)

    def contour_drawer(self):
        self.script.write("""
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
        """.format(Fill=self.FillOn, Lines=self.LinesOn, Label=self.LabelsOn))

        if self.Sym_color:
            self.script.write("""
            symMinMaxPlt({variable_slice},13,False,cnres)
        """.format(variable_slice=self.variable_slice_0))

        if self.Set_contour_levels:
            self.script.write("""
            cnres@cnLevelSelectionMode="ManualLevels"
            cnres@cnMaxLevelValF={max}
            cnres@cnMinLevelValF={min}
            cnres@cnLevelSpacingF={spacing}
        """.format(max=self.contour_levels[0], min=self.contour_levels[1], spacing=self.contour_levels[2]))

        if self.Scale:
            self.script.write("""
            cnres@tiMainFontHeightF=0.02
            cnres@tiMainString="{standard}"+tostring(lev)+" (10~S~-{power}~N~"+variable@units+")"+"     "+cd_string(time(0), \\
                            "%H%MUTC %d%c %Y")
            """.format(standard=self.variable_standard_name, power=int(self.power_scale)))
        else:
            self.script.write("""
            cnres@tiMainFontHeightF=0.02
            cnres@tiMainString="{standard}"+tostring(lev)+" ("+variable@units+")"+"     "+cd_string(time(0), \\
                                "%H%MUTC %d%c %Y")
                """.format(standard=self.variable_standard_name))

        self.script.write("""
            map=gsn_csm_contour_map(wks, {variable_slice}, cnres)
        """.format(variable_slice=self.variable_slice_0))

    def orography_drawer(self):
        self.script.write("""
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
        """.format(topo=self.topo_line))

        self.script.write("""
            map2=gsn_csm_contour(wks,z({{zlllat:zurlat}},{{zlllon:zurlon}}),tpres)
            overlay(map,map2)
            draw(map)
            frame(wks)
        """.format(topo=self.topo_line, standard=self.variable_standard_name))

    def time_iterator(self):
        if self.Scale:
            self.script.write("""
                nmos=ntime
                do nmo=1,nmos-1
                    month=nmo+1
                    cnres@tiMainString="{standard}"+tostring(lev)+" (10~S~-{power}~N~"+variable@units+")"+"     "+cd_string(time(nmo), \\
                                    "%H%MUTC %d%c %Y")
                    cnres@tiMainFontHeightF=0.02
            """.format(standard=self.variable_standard_name, power=int(self.power_scale)))
        else:
            self.write("""
                nmos=ntime
                do nmo=1,nmos-1
                    month=nmo+1
                    cnres@tiMainString="{standard}"+tostring(lev)+" ("+variable@units+")"+"     "+cd_string(time(nmo), \\
                                        "%H%MUTC %d%c %Y")
                    cnres@tiMainFontHeightF=0.02
            """.format(standard=self.variable_standard_name))

        if self.Sym_color:
            self.script.write("""
                symMinMaxPlt({variable_slice},13, False,cnres)
        """.format(variable_slice=self.variable_slice_n))

        self.script.write("""
                map=gsn_csm_contour_map(wks, {variable_slice},cnres)
                map2=gsn_csm_contour(wks,z({{zlllat:zurlat}},{{zlllon:zurlon}}),tpres)
                overlay(map,map2)

                draw(map)
                frame(wks)
            end do
        """.format(variable_slice=self.variable_slice_n))


    def ender(self):
        self.script.write("""
            delete(variable)

            end""")

    def close(self):
        self.script.close()



    def output_script(self):
        self.script_creator()
        self.header()
        self.parameter_define()
        self.variable_reader()
        self.orography_setter()
        self.contour_drawer()
        self.orography_drawer()
        self.time_iterator()
        self.ender()
        self.close()
