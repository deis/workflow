SET GO15VENDOREXPERIMENT=1
go build -a -installsuffix cgo -ldflags '-s' -o deis.exe .
