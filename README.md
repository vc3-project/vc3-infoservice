# vc3-infoservice

A client/server framework for implementing distributed systems. 

Includes implicit Object-Relation Mapping.

Includes inter-component security. 

Provides Access Control List (ACL) support for system entities. 

Does not require an underlying database but supports it via plugin. 

Does not require an external web server but compatible with one. 


# Notes

CherryPy Version 3.2.2 required, otherwise SSL doesn't work. 

Source RPM (rebuildable for RHEL6,7 and Fedora) here:
  http://dev.racf.bnl.gov/dist/vc3/

Do rpmbuild --rebuild python-cherrypy-3.2.2-4.el7.src.rpm