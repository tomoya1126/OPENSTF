// ost_datalib.h
#ifndef _OST_DATALIB_H_
#define _OST_DATALIB_H_
extern void ost_init(void);
extern void ost_section_size(int);
extern void ost_unit_size(int);
extern void ost_1d_size(int);
extern void ost_2d_size(int);
extern void ost_title(const char []);
extern void ost_xsection1(double);
extern void ost_ysection1(double);
extern void ost_zsection1(double);
extern void ost_xdivision1(int);
extern void ost_ydivision1(int);
extern void ost_zdivision1(int);
extern void ost_xsection(int, ...);
extern void ost_ysection(int, ...);
extern void ost_zsection(int, ...);
extern void ost_xdivision(int, ...);
extern void ost_ydivision(int, ...);
extern void ost_zdivision(int, ...);
extern void ost_volt(double);
extern void ost_volt_name(const char []);
extern void ost_epsr(double);
extern void ost_epsr_name(const char []);
extern void ost_unit(int, int, int, const double []);
extern void ost_unit6(int, int, int, double, double, double, double, double, double);
extern void ost_unit_name(const char []);
extern void ost_solver(double, int, int, double);
extern void ost_plotiter(void);
extern void ost_plot1d(const char [], const char [], double, double);
extern void ost_1ddb(void);
extern void ost_1dscale(double, double, int);
extern void ost_1dlog(int);
extern void ost_plot2d(const char [], const char [], double);
extern void ost_2dfigure(int, int);
extern void ost_2ddb(void);
extern void ost_2dscale(double, double);
extern void ost_2dcontour(int);
extern void ost_2dobject(int, int);
extern void ost_2dzoom(double, double, double, double);
extern void ost_2dlog(int);
extern void ost_outdata(const char []);
#endif  // _OST_DATALIB_H_
