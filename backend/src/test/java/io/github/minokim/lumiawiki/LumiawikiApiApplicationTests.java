package io.github.minokim.lumiawiki;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;
import org.testcontainers.postgresql.PostgreSQLContainer;

@SpringBootTest(
    classes = io.github.minokim.lumiawiki.fixture.FoundationTestApplication.class,
    properties = "spring.flyway.locations=classpath:db/test-migration")
@ActiveProfiles("test")
@Tag("integration")
@Import(LumiawikiApiApplicationTests.Database.class)
class LumiawikiApiApplicationTests {

  @TestConfiguration(proxyBeanMethods = false)
  static class Database {
    @Bean
    @ServiceConnection
    PostgreSQLContainer postgres() {
      return new PostgreSQLContainer("postgres:18.6")
          .withDatabaseName("lumiawiki_test")
          .withUsername("test")
          .withPassword("test")
          .withReuse(false);
    }
  }

  @Autowired JdbcTemplate jdbc;

  @Test
  void contextLoads() {
    assertEquals("lumiawiki_test", jdbc.queryForObject("select current_database()", String.class));
    assertNotEquals("lumiawiki", jdbc.queryForObject("select current_database()", String.class));
  }

  @Test
  @Transactional
  void flywayTestFixtureSupportsJdbcRoundTrip() {
    jdbc.update("insert into test_connection_probe(id, marker) values (?, ?)", 1, "isolated");
    assertEquals(
        "isolated",
        jdbc.queryForObject(
            "select marker from test_connection_probe where id = ?", String.class, 1));
  }
}
