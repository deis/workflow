package parser

import (
	"github.com/deis/workflow/client/cmd"
	docopt "github.com/docopt/docopt-go"
)

// Certs routes certs commands to their specific function.
func Certs(argv []string) error {
	usage := `
Valid commands for certs:

certs:list            list SSL certificates for an app
certs:add             add an SSL certificate to an app
certs:remove          remove an SSL certificate from an app
certs:info            get detailed informaton about the certificate
certs:attach          attach an SSL certificate to a domain
certs:detach          detach an SSL certificate from a domain

Use 'deis help [command]' to learn more.
`

	switch argv[0] {
	case "certs:list":
		return certsList(argv)
	case "certs:add":
		return certAdd(argv)
	case "certs:remove":
		return certRemove(argv)
	case "certs:info":
		return certInfo(argv)
	case "certs:attach":
		return certAttach(argv)
	case "certs:detach":
		return certDetach(argv)
	default:
		if printHelp(argv, usage) {
			return nil
		}

		if argv[0] == "certs" {
			argv[0] = "certs:list"
			return certsList(argv)
		}

		PrintUsage()
		return nil
	}
}

func certsList(argv []string) error {
	usage := `
Show certificate information for an SSL application.

Usage: deis certs:list [options]

Options:
  -l --limit=<num>
    the maximum number of results to display, defaults to config setting
`

	args, err := docopt.Parse(usage, argv, true, "", false, true)
	if err != nil {
		return err
	}

	results, err := responseLimit(safeGetValue(args, "--limit"))
	if err != nil {
		return err
	}

	return cmd.CertsList(results)
}

func certAdd(argv []string) error {
	usage := `
Binds a certificate/key pair to an application.

Usage: deis certs:add <name> <cert> <key> [options]

Arguments:
  <name>
    Name of the certificate to reference it by.
  <cert>
    The public key of the SSL certificate.
  <key>
    The private key of the SSL certificate.
`

	args, err := docopt.Parse(usage, argv, true, "", false, true)
	if err != nil {
		return err
	}

	name := args["<name>"].(string)
	cert := args["<cert>"].(string)
	key := args["<key>"].(string)

	return cmd.CertAdd(cert, key, name)
}

func certRemove(argv []string) error {
	usage := `
removes a certificate/key pair from the application.

Usage: deis certs:remove <name> [options]

Arguments:
  <name>
    the name of the cert to remove from the app.
`

	args, err := docopt.Parse(usage, argv, true, "", false, true)
	if err != nil {
		return err
	}

	return cmd.CertRemove(safeGetValue(args, "<name>"))
}

func certInfo(argv []string) error {
	usage := `
fetch more detailed information about a certificate

Usage: deis certs:info <name> [options]

Arguments:
  <name>
    the name of the cert to get information from
`

	args, err := docopt.Parse(usage, argv, true, "", false, true)
	if err != nil {
		return err
	}

	return cmd.CertInfo(safeGetValue(args, "<name>"))
}

func certAttach(argv []string) error {
	usage := `
attach a certificate to a domain.

Usage: deis certs:attach <name> <domain> [options]

Arguments:
  <name>
    name of the certificate to attach domain to
  <domain>
    common name of the domain to attach to (needs to already be in the system)
`

	args, err := docopt.Parse(usage, argv, true, "", false, true)
	if err != nil {
		return err
	}

	name := safeGetValue(args, "<name>")
	domain := safeGetValue(args, "<domain>")
	return cmd.CertAttach(name, domain)
}

func certDetach(argv []string) error {
	usage := `
detach a certificate from a domain.

Usage: deis certs:detach <name> <domain> [options]

Arguments:
  <name>
    name of the certificate to deatch from a domain
  <domain>
    common name of the domain to detach from
`

	args, err := docopt.Parse(usage, argv, true, "", false, true)
	if err != nil {
		return err
	}

	name := safeGetValue(args, "<name>")
	domain := safeGetValue(args, "<domain>")
	return cmd.CertDetach(name, domain)
}
