public class GetJavaVersion {
    public static void main(String[] args) {
        System.out.println("os.arch=\"" + System.getProperty("os.arch") + "\"");
        System.out.println("java.version=\"" + System.getProperty("java.version") + "\"");
        System.out.println("java.vendor=\"" + System.getProperty("java.vendor") + "\"");
    }
}