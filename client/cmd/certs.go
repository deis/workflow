package cmd

import (
	"fmt"
	"io/ioutil"
	"os"
	"strings"
	"time"

	"github.com/olekukonko/tablewriter"

	"github.com/deis/workflow/client/controller/client"
	"github.com/deis/workflow/client/controller/models/certs"
)

// CertsList lists certs registered with the controller.
func CertsList(results int) error {
	c, err := client.New()

	if err != nil {
		return err
	}

	if results == defaultLimit {
		results = c.ResponseLimit
	}

	certList, _, err := certs.List(c, results)

	if err != nil {
		return err
	}

	if len(certList) == 0 {
		fmt.Println("No certs")
		return nil
	}

	table := tablewriter.NewWriter(os.Stdout)
	table.SetAlignment(tablewriter.ALIGN_LEFT)
	table.SetBorder(false)
	table.SetAutoFormatHeaders(false)
	table.SetHeaderLine(true)
	table.SetHeader([]string{"Name", "Common Name", "SubjectAltName", "Expires", "Fingerprint", "Domains", "Updated", "Created"})
	for _, cert := range certList {
		domains := strings.Join(cert.Domains[:], ",")
		san := strings.Join(cert.SubjectAltName[:], ",")

		// Make dates more readable
		now := time.Now()
		expires := cert.Expires.Time.Format("2 Jan 2006")
		created := cert.Created.Time.Format("2 Jan 2006")
		updated := cert.Updated.Time.Format("2 Jan 2006")

		if cert.Expires.Time.Before(now) {
			expires += " (expired)"
		} else {
			// Ghetto solution
			expires += " (in"
			year := cert.Expires.Time.Year() - now.Year()
			month := cert.Expires.Time.Month() - now.Month()
			day := cert.Expires.Time.Day() - now.Day()

			if year > 0 {
				expires += fmt.Sprintf(" %d year", year)
				if year > 1 {
					expires += "s"
				}
			} else if month > 0 {
				expires += fmt.Sprintf(" %d month", month)
				if month > 1 {
					expires += "s"
				}
			} else if day != 0 {
				// special handling on negative days
				if day < 0 {
					day *= -1
				}

				expires += fmt.Sprintf(" %d day", day)
				if day > 1 {
					expires += "s"
				}
			}
			expires += ")"
		}

		// show a shorter version of the fingerprint
		fingerprint := cert.Fingerprint[:5] + "[...]" + cert.Fingerprint[len(cert.Fingerprint)-5:]

		table.Append([]string{cert.Name, cert.CommonName, san, expires, fingerprint, domains, updated, created})
	}
	table.Render()

	return nil
}

// CertAdd adds a cert to the controller.
func CertAdd(cert string, key string, name string) error {
	c, err := client.New()

	if err != nil {
		return err
	}

	fmt.Print("Adding SSL endpoint... ")
	quit := progress()
	err = doCertAdd(c, cert, key, name)
	quit <- true
	<-quit

	if err != nil {
		return err
	}

	fmt.Println("done")
	return nil
}

func doCertAdd(c *client.Client, cert string, key string, name string) error {
	certFile, err := ioutil.ReadFile(cert)
	if err != nil {
		return err
	}

	keyFile, err := ioutil.ReadFile(key)
	if err != nil {
		return err
	}

	_, err = certs.New(c, string(certFile), string(keyFile), name)
	return err
}

// CertRemove deletes a cert from the controller.
func CertRemove(name string) error {
	c, err := client.New()
	if err != nil {
		return err
	}

	fmt.Printf("Removing %s... ", name)
	quit := progress()

	certs.Delete(c, name)

	quit <- true
	<-quit

	if err == nil {
		fmt.Println("done")
	}

	return err
}

// CertInfo gets info about certficiate
func CertInfo(name string) error {
	c, err := client.New()
	if err != nil {
		return err
	}

	cert, err := certs.Get(c, name)
	if err != nil {
		return err
	}

	domains := strings.Join(cert.Domains[:], ",")
	if domains == "" {
		domains = "No connected domains"
	}

	san := strings.Join(cert.SubjectAltName[:], ",")
	if san == "" {
		san = "N/A"
	}

	fmt.Printf("=== %s Certificate\n", cert.Name)
	fmt.Println("Common Name(s):    ", cert.CommonName)
	fmt.Println("Expires At:        ", cert.Expires)
	fmt.Println("Starts At:         ", cert.Starts)
	fmt.Println("Fingerprint:       ", cert.Fingerprint)
	fmt.Println("Subject Alt Name:  ", san)
	fmt.Println("Issuer:            ", cert.Issuer)
	fmt.Println("Subject:           ", cert.Subject)
	fmt.Println()
	fmt.Println("Connected Domains: ", domains)
	fmt.Println("Owner:             ", cert.Owner)
	fmt.Println("Created:           ", cert.Created)
	fmt.Println("Updated:           ", cert.Updated)

	return nil
}

// CertAttach attaches a certificate to a domain
func CertAttach(name string, domain string) error {
	c, err := client.New()

	if err != nil {
		return err
	}

	fmt.Printf("Attaching certificate %s to domain %s... ", name, domain)
	quit := progress()

	certs.Attach(c, name, domain)

	quit <- true
	<-quit

	if err == nil {
		fmt.Println("done")
	}

	return err
}

// CertDetach detaches a certificate from a domain
func CertDetach(name string, domain string) error {
	c, err := client.New()

	if err != nil {
		return err
	}

	fmt.Printf("Detaching certificate %s from domain %s... ", name, domain)
	quit := progress()

	certs.Detach(c, name, domain)

	quit <- true
	<-quit

	if err == nil {
		fmt.Println("done")
	}

	return err
}
