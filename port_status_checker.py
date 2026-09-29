import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_port(host, port, timeout):
    """Return the port status: Open, Closed, or Filtered."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            return "Open"
        return "Closed"
    except socket.timeout:
        return "Filtered"
    except OSError:
        return "Filtered"
    finally:
        sock.close()

def scan_ports(host, start_port, end_port, timeout):
    results = {}
    ports = range(start_port, end_port + 1)

    with ThreadPoolExecutor(max_workers=20) as executor:
        jobs = {
            executor.submit(check_port, host, port, timeout): port
            for port in ports
        }
        for job in as_completed(jobs):
            port = jobs[job]
            results[port] = job.result()

    return results

def main():
    parser = argparse.ArgumentParser(
        description="Authorized TCP port status checker"
    )
    parser.add_argument("host", help="Target hostname or IP address")
    parser.add_argument("start_port", type=int, help="First TCP port")
    parser.add_argument("end_port", type=int, help="Last TCP port")
    parser.add_argument("--timeout", type=float, default=0.5,
                        help="Connection timeout in seconds")
    args = parser.parse_args()

    if not (1 <= args.start_port <= args.end_port <= 65535):
        parser.error("Port range must be between 1 and 65535.")

    print(f"Port Status Checker")
    print(f"Target : {args.host}")
    print(f"Range  : {args.start_port}-{args.end_port}")
    print("-" * 42)

    results = scan_ports(
        args.host, args.start_port, args.end_port, args.timeout
    )

    print(f"{'Port':<8}{'Status':<12}")
    print("-" * 20)
    for port in sorted(results):
        print(f"{port:<8}{results[port]:<12}")

    counts = {
        "Open": sum(v == "Open" for v in results.values()),
        "Closed": sum(v == "Closed" for v in results.values()),
        "Filtered": sum(v == "Filtered" for v in results.values()),
    }

    print("-" * 20)
    print(
        f"Summary: Open={counts['Open']}, "
        f"Closed={counts['Closed']}, Filtered={counts['Filtered']}"
    )

if __name__ == "__main__":
    main()
