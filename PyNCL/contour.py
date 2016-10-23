#!/home/meteoboy4/anaconda/bin/python

import math


class CommonPlot(object):
    def __init__(self, **kwargs):
        prop_defaults = {
            "pname": "div",
            "fmt": "ps",
            "lllat": -10.,
            "lllon": 20.,
            "urlat": 60.,
            "urlon": 160.,
            "background_directory": "/run/media/MeteoBoy4/Data/MData/ERA-Interim/Surface_GeoP/",
            "topo_line": 2000.,
            "zlllat": 20.,
            "zlllon": 60.,
            "zurlat": 45.,
            "zurlon": 110.
        }

        for (prop, default) in prop_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))

    def header(self):
        return """load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"

begin
;------Define constants and parameters
"""

    def parameter_define(self):
        return """
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
        """.format(pname=self.pname, fmt=self.fmt, lllat=self.lllat, lllon=self.lllon, urlat=self.urlat,
               urlon=self.urlon, zlllat=self.zlllat, zlllon=self.zlllon, zurlat=self.zurlat, zurlon=self.zurlon)

    def variable_reader(self):
        return """
;------Read the data from ncfile and some other supporting data
        dirbac   = "{dirbac}"
        maskf=addfile("$NCARG_ROOT/lib/ncarg/data/cdf/landsea.nc","r")
        system("rm -f "+pname+"."+fmt)
        ofile = addfile(dirbac+"Surface_GeoP.nc","r")
        z=short2flt(ofile->z(0,:,:))
        lsdata=maskf->LSMASK
        """.format(dirbac=self.background_directory)

    def supporting_data(self):
        return """
        time = Vfile->time
        printVarSummary(variable)
        dims=dimsizes(variable)
        ntime=dims(0)
        """

    def orography_setter(self):
        return """
;------Set for orography and masking the ocean
        z=z/9.80665
        lsm=landsea_mask(lsdata,z&latitude,z&longitude)
        z=mask(z,lsm.eq.0,False)
        """

    def orography_drawer(self):
        return """
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

        orography=gsn_csm_contour(wks,z({{zlllat:zurlat}},{{zlllon:zurlon}}),tpres)
        """.format(topo=self.topo_line)

    def overlay(self, base, transform):
        return """
        overlay({base},{transform})
        """.format(base=base, transform=transform)

    def draw_frame(self, base):
        return """
        draw({base})
        frame(wks)
        """.format(base=base)

    def deleter(self, variable):
        return """
        delete({variable})
        """.format(variable=variable)

    def terminator(self):
        return """

end"""

class Contour(object):
    def __init__(self, inputs, **kwargs):
        prop_defaults = {
            "levels_exist": False,
            "level": 300,
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
            "Shorts": True
        }

        self.input = inputs
        self.common = CommonPlot(**kwargs)

        for (prop, default) in prop_defaults.iteritems():
            setattr(self, prop, kwargs.get(prop, default))

        self.power_scale = math.ceil(math.log(self.scale, 10.))

        if self.levels_exist:
            self.variable_slice_0 = 'variable(0, {lev}, {lllat:urlat}, {lllon:urlon})'
            self.variable_slice_n = 'variable(nmo, {lev}, {lllat:urlat}, {lllon:urlon})'
        else:
            self.variable_slice_0 = 'variable(0, {lllat:urlat}, {lllon:urlon})'
            self.variable_slice_n = 'variable(nmo, {lllat:urlat}, {lllon:urlon})'

    # def script_creator(self):
    #     self.script = open('contour.ncl', 'w')

    def header(self):
        return self.common.header()

    def parameter_define(self):
        script1 = """
        lev     = {lev}
        """.format(lev=self.level)
        script2 = self.common.parameter_define()

        return script1 + script2

    def variable_reader(self):
        script1 = self.common.variable_reader()
        script2 = """
        dirvar   = "{dirvar}"
        Vfile    = addfile(dirvar,"r")
        """.format(dirvar=self.input)

        if self.Shorts:
            script3 = 'variable = short2flt(Vfile->{vari})'.format(vari=self.variable_name)
        else:
            script3 = 'variable = Vfile->{vari}'.format(vari=self.variable_name)

        script3s = ''
        if self.Scale:
            script3s = """
        variable = variable*{scale}""".format(scale=self.scale)

        return script1 + script2 + script3 + script3s

    def supporting_data(self):
        return self.common.supporting_data()

    def orography_setter(self):
        return self.common.orography_setter()

    def contour_drawer(self):
        script1 = """
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
        """.format(Fill=self.FillOn, Lines=self.LinesOn, Label=self.LabelsOn)

        script2 = ''
        if self.Sym_color:
            script2 = """
        symMinMaxPlt({variable_slice},13,False,cnres)
        """.format(variable_slice=self.variable_slice_0)

        if self.Set_contour_levels:
            script2 = """
        cnres@cnLevelSelectionMode="ManualLevels"
        cnres@cnMaxLevelValF={max}
        cnres@cnMinLevelValF={min}
        cnres@cnLevelSpacingF={spacing}
        """.format(max=self.contour_levels[0], min=self.contour_levels[1], spacing=self.contour_levels[2])

        if self.Scale:
            script3 = """
        cnres@tiMainFontHeightF=0.02
        cnres@tiMainString="{standard}"+tostring(lev)+" (10~S~-{power}~N~"+variable@units+")"+"     "+cd_string(time(0), \\
                        "%H%MUTC %d%c %Y")
            """.format(standard=self.variable_standard_name, power=int(self.power_scale))
        else:
            script3 = """
        cnres@tiMainFontHeightF=0.02
        cnres@tiMainString="{standard}"+tostring(lev)+" ("+variable@units+")"+"     "+cd_string(time(0), \\
                            "%H%MUTC %d%c %Y")
                """.format(standard=self.variable_standard_name)

        script4 = """
        contourplot=gsn_csm_contour_map(wks, {variable_slice}, cnres)
        """.format(variable_slice=self.variable_slice_0)

        return script1 + script2 + script3 + script4

    def orography_drawer(self):
        return self.common.orography_drawer()

    def overlay(self):
        return self.common.overlay('contourplot', 'orography')

    def draw_frame(self):
        return self.common.draw_frame('contourplot')

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
            contourplot=gsn_csm_contour_map(wks, {variable_slice},cnres)
            orography=gsn_csm_contour(wks,z({{zlllat:zurlat}},{{zlllon:zurlon}}),tpres)
            overlay(contourplot,orography)

            draw(contourplot)
            frame(wks)
        end do
        """.format(variable_slice=self.variable_slice_n))

    def deleter(self):
        return self.common.deleter('variable')

    def terminator(self):
        return self.common.terminator()

    def output_script(self):
        ncl_script = open('contour.ncl', 'w')
        ncl_script.write(self.header())
        ncl_script.write(self.parameter_define())
        ncl_script.write(self.variable_reader())
        ncl_script.write(self.supporting_data())
        ncl_script.write(self.orography_setter())
        ncl_script.write(self.contour_drawer())
        ncl_script.write(self.orography_drawer())
        ncl_script.write(self.overlay())
        ncl_script.write(self.draw_frame())
        # self.time_iterator()
        ncl_script.write(self.deleter())
        ncl_script.write(self.terminator())
        ncl_script.close()


# class ContourWithVector(object):
#
#     def __init__(self, contourvar, uvar, vvar, uname='u', vname='v', **kwargs):
#         self.contour = Contour(contourvar, **kwargs)
#         self.uvar = uvar
#         self.vvar = vvar
#         self.uname = uname
#         self.vname = vname
#
#     def script_creator(self):
#         self.script = open('cv.ncl', 'w')
#
#     def header(self):
#         self.contour.header()
#
#     def parameter_define(self):
#         self.contour.parameter_define()
#
#     def variable_reader(self):
#         self.contour.variable_reader()
#         self.script.write("""
# ;--------------Vector-related part
#         diru = "{uvar}"
#         dirv = "{vvar}"
#         Ufile = addfile(diru, "r")
#         Vfile = addfile(dirv, "r")
#         """.format(uvar=self.uvar, vvar=self.vvar))
#
#         if self.Shorts:
#             self.script.write('u = short2flt(Ufile->{vari})'.format(vari=self.uname))
#             self.script.write('v = short2flt(Vfile->{vari})'.format(vari=self.vname))
#         else:
#             self.script.write('u = Ufile->{vari}'.format(vari=self.uname))
#             self.script.write('v = Vfile->{vari}'.format(vari=self.vname))
#
#         self.script.write("""
#         wind=u
#         wind=sqrt(u*u+v*v)
#         """)
#
#     def orography_setter(self):
#         self.contour.orography_setter()